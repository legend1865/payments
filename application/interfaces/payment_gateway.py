from typing import Protocol
from uuid import UUID

from application.dto import Payment


class PaymentGateway(Protocol):
    async def add(self, payment: Payment) -> None: ...

    async def get_by_id(self, payment_id: UUID) -> Payment | None: ...

    async def get_by_idempotency_key(self, idempotency_key: str) -> Payment | None: ...
