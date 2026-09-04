from uuid import UUID

from application.dto import Payment
from application.exceptions import PaymentNotFoundError
from application.interfaces import PaymentGateway


class GetPaymentInteractor:
    def __init__(self, payment_gateway: PaymentGateway) -> None:
        self._payment_gateway = payment_gateway

    async def __call__(self, payment_id: UUID) -> Payment:
        payment = await self._payment_gateway.get_by_id(payment_id)
        if payment is None:
            raise PaymentNotFoundError
        return payment
