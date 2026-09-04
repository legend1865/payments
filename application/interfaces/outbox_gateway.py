from datetime import datetime
from typing import Protocol
from uuid import UUID

from application.dto import OutboxMessage


class OutboxGateway(Protocol):
    async def add(self, message: OutboxMessage) -> None: ...

    async def get_unpublished(self, limit: int) -> list[OutboxMessage]: ...

    async def mark_as_published(self, message_id: UUID, published_at: datetime) -> None: ...
