from infrastructure.config import load_config_from_env
from infrastructure.database import create_engine, create_session_factory
from infrastructure.webhook import HttpxWebhookGateway
from presentation.amqp_api.consumer import register_payment_consumer
from presentation.amqp_api.queues import payments_dlq_queue, payments_retry_queue

import httpx
from faststream import FastStream
from faststream.rabbit import RabbitBroker


config = load_config_from_env()
engine = create_engine(config.DATABASE_URL)
session_factory = create_session_factory(engine)
broker = RabbitBroker(config.RABBITMQ_URL)
http_client = httpx.AsyncClient(timeout=config.WEBHOOK_TIMEOUT)
webhook_gateway = HttpxWebhookGateway(http_client)
retry_publisher = broker.publisher(queue=payments_retry_queue, persist=True)
dlq_publisher = broker.publisher(queue=payments_dlq_queue, persist=True)

register_payment_consumer(
    broker,
    config=config,
    session_factory=session_factory,
    webhook_gateway=webhook_gateway,
    retry_publisher=retry_publisher,
    dlq_publisher=dlq_publisher,
)

app = FastStream(broker)


@app.on_shutdown
async def close_resources() -> None:
    await http_client.aclose()
    await engine.dispose()
