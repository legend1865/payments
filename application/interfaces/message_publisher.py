from typing import Protocol

from application.dto import OutboxMessage


class MessagePublisher(Protocol):
    async def publish(self, message: OutboxMessage) -> None: ...
