import asyncio
import random
from dataclasses import replace
from datetime import UTC, datetime
from uuid import UUID

from application.dto import Payment, PaymentStatus
from application.exceptions import PaymentNotFoundError
from application.interfaces import PaymentGateway, TransactionManager, WebhookGateway


class ProcessPaymentInteractor:
    def __init__(
        self,
        transaction_manager: TransactionManager,
        payment_gateway: PaymentGateway,
        webhook_gateway: WebhookGateway,
        success_probability: float,
        processing_delay: tuple[float, float],
    ) -> None:
        self._transaction_manager = transaction_manager
        self._payment_gateway = payment_gateway
        self._webhook_gateway = webhook_gateway
        self._success_probability = success_probability
        self._processing_delay = processing_delay

    async def __call__(self, payment_id: UUID) -> Payment:
        async with self._transaction_manager.start_transaction():
            payment = await self._payment_gateway.get_by_id(payment_id)
            if payment is None:
                raise PaymentNotFoundError

            if payment.status is PaymentStatus.PENDING:
                await asyncio.sleep(
                    random.uniform(*self._processing_delay),  # noqa: S311
                )
                status = (
                    PaymentStatus.SUCCEEDED
                    if random.random() < self._success_probability  # noqa: S311
                    else PaymentStatus.FAILED
                )
                processed_at = datetime.now(UTC)
                await self._payment_gateway.update_status(payment.id, status, processed_at)
                await self._transaction_manager.commit()
                payment = replace(payment, status=status, processed_at=processed_at)

        await self._webhook_gateway.send(payment)
        return payment
