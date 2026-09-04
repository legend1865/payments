from application.dto import OutboxMessage

from faststream.rabbit import RabbitBroker, RabbitQueue


class FastStreamMessagePublisher:
    def __init__(self, broker: RabbitBroker, queue: RabbitQueue) -> None:
        self._broker = broker
        self._queue = queue

    async def publish(self, message: OutboxMessage) -> None:
        await self._broker.publish(
            message.payload,
            queue=self._queue,
            persist=True,
            message_id=str(message.id),
        )
