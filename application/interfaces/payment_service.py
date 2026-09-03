from typing import Protocol
from uuid import UUID

from application.dto import CreatePaymentCommand, Payment


class PaymentService(Protocol):
    async def create_payment(self, command: CreatePaymentCommand) -> Payment: ...

    async def get_payment(self, payment_id: UUID) -> Payment:
        """Return a payment or raise PaymentNotFoundError."""
        ...
