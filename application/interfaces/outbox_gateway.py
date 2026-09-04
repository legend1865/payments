from typing import Protocol

from application.dto import OutboxMessage


class OutboxGateway(Protocol):
    async def add(self, message: OutboxMessage) -> None: ...
