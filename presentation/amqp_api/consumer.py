import logging
from datetime import timedelta
from typing import Any, Protocol

from application.dto import PaymentCreatedEvent
from application.interfaces import WebhookGateway
from infrastructure.config import Config
from infrastructure.container import create_process_payment_interactor
from presentation.amqp_api.queues import payments_new_queue

from faststream import AckPolicy
from faststream.rabbit import RabbitBroker, RabbitMessage
from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker


logger = logging.getLogger(__name__)


class MessagePublisher(Protocol):
    async def publish(
        self,
        message: dict[str, Any],
        *,
        headers: dict[str, int | str],
        expiration: timedelta | None = None,
    ) -> Any: ...


def register_payment_consumer(
    broker: RabbitBroker,
    *,
    config: Config,
    session_factory: async_sessionmaker[AsyncSession],
    webhook_gateway: WebhookGateway,
    retry_publisher: MessagePublisher,
    dlq_publisher: MessagePublisher,
) -> None:
    @broker.subscriber(queue=payments_new_queue, ack_policy=AckPolicy.MANUAL)
    async def process_payment(event: PaymentCreatedEvent, message: RabbitMessage) -> None:
        try:
            async with session_factory() as session:
                interactor = create_process_payment_interactor(
                    session,
                    webhook_gateway,
                    success_probability=config.SUCCESS_PROBABILITY,
                    processing_delay=(
                        config.PAYMENT_PROCESSING_MIN_DELAY,
                        config.PAYMENT_PROCESSING_MAX_DELAY,
                    ),
                )
                await interactor(event.payment_id)
        except Exception as error:
            logger.exception("Payment processing failed", extra={"payment_id": str(event.payment_id)})
            await _retry_or_move_to_dlq(
                event,
                message,
                error,
                config=config,
                retry_publisher=retry_publisher,
                dlq_publisher=dlq_publisher,
            )
        else:
            await message.ack()


async def _retry_or_move_to_dlq(
    event: PaymentCreatedEvent,
    message: RabbitMessage,
    error: Exception,
    *,
    config: Config,
    retry_publisher: MessagePublisher,
    dlq_publisher: MessagePublisher,
) -> None:
    retry_count = int(message.headers.get(config.RETRY_COUNT_HEADER, 0))
    attempt = retry_count + 1
    headers = {
        config.RETRY_COUNT_HEADER: attempt,
        config.ERROR_TYPE_HEADER: type(error).__name__,
    }

    try:
        if attempt < config.MAX_ATTEMPTS:
            delay = timedelta(seconds=2**retry_count)
            await retry_publisher.publish(
                event.model_dump(mode="json"),
                headers=headers,
                expiration=delay,
            )
        else:
            await dlq_publisher.publish(
                event.model_dump(mode="json"),
                headers=headers,
            )
    except Exception:
        await message.nack(requeue=True)
        raise

    await message.ack()
