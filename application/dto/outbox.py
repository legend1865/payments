from dataclasses import dataclass
from datetime import datetime
from typing import Any
from uuid import UUID


@dataclass(frozen=True, slots=True)
class OutboxMessage:
    id: UUID
    event_name: str
    payload: dict[str, Any]
    created_at: datetime
    published_at: datetime | None
