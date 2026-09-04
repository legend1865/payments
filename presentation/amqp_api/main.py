import asyncio
import logging

from infrastructure.config import Settings
from infrastructure.container import create_publish_outbox_interactor
from infrastructure.database import create_engine, create_session_factory
from infrastructure.messaging import FastStreamMessagePublisher
from presentation.amqp_api.queues import payments_new_queue

from faststream.rabbit import RabbitBroker


logger = logging.getLogger(__name__)


async def run() -> None:
    settings = Settings()
    engine = create_engine(settings.database_url)
    session_factory = create_session_factory(engine)
    broker = RabbitBroker(settings.rabbitmq_url)

    await broker.connect()
    await broker.declare_queue(payments_new_queue)
    message_publisher = FastStreamMessagePublisher(broker, payments_new_queue)
    try:
        while True:
            try:
                async with session_factory() as session:
                    interactor = create_publish_outbox_interactor(session, message_publisher)
                    await interactor(settings.outbox_batch_size)
            except asyncio.CancelledError:
                raise
            except Exception:
                logger.exception("Failed to publish outbox messages")

            await asyncio.sleep(settings.outbox_poll_interval)
    finally:
        await broker.close()
        await engine.dispose()


if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO)
    asyncio.run(run())
