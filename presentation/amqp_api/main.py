import asyncio
import logging

from infrastructure.config import load_config_from_env
from infrastructure.container import create_publish_outbox_interactor
from infrastructure.database import create_engine, create_session_factory
from infrastructure.messaging import FastStreamMessagePublisher
from presentation.amqp_api.queues import payments_new_queue

from faststream.rabbit import RabbitBroker


logger = logging.getLogger(__name__)


async def run() -> None:
    config = load_config_from_env()
    engine = create_engine(config.DATABASE_URL)
    session_factory = create_session_factory(engine)
    broker = RabbitBroker(config.RABBITMQ_URL)

    await broker.connect()
    await broker.declare_queue(payments_new_queue)
    message_publisher = FastStreamMessagePublisher(broker, payments_new_queue)
    try:
        while True:
            try:
                async with session_factory() as session:
                    interactor = create_publish_outbox_interactor(session, message_publisher)
                    await interactor(config.OUTBOX_BATCH_SIZE)
            except asyncio.CancelledError:
                raise
            except Exception:
                logger.exception("Failed to publish outbox messages")

            await asyncio.sleep(config.OUTBOX_POLL_INTERVAL)
    finally:
        await broker.close()
        await engine.dispose()


if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO)
    asyncio.run(run())
