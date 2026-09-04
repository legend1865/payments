from datetime import UTC, datetime

from application.interfaces import MessagePublisher, OutboxGateway, TransactionManager


class PublishOutboxInteractor:
    def __init__(
        self,
        transaction_manager: TransactionManager,
        outbox_gateway: OutboxGateway,
        message_publisher: MessagePublisher,
    ) -> None:
        self._transaction_manager = transaction_manager
        self._outbox_gateway = outbox_gateway
        self._message_publisher = message_publisher

    async def __call__(self, limit: int) -> int:
        async with self._transaction_manager.start_transaction():
            messages = await self._outbox_gateway.get_unpublished(limit)

            for message in messages:
                await self._message_publisher.publish(message)
                await self._outbox_gateway.mark_as_published(message.id, datetime.now(UTC))

            await self._transaction_manager.commit()
            return len(messages)
