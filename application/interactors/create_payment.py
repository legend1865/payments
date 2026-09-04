from datetime import UTC, datetime
from uuid import uuid4

from application.dto import CreatePaymentCommand, OutboxMessage, Payment, PaymentCreatedEvent, PaymentStatus
from application.interfaces import OutboxGateway, PaymentGateway, TransactionManager


PAYMENT_CREATED_EVENT = "payments.new"


class CreatePaymentInteractor:
    def __init__(
        self,
        transaction_manager: TransactionManager,
        payment_gateway: PaymentGateway,
        outbox_gateway: OutboxGateway,
    ) -> None:
        self._transaction_manager = transaction_manager
        self._payment_gateway = payment_gateway
        self._outbox_gateway = outbox_gateway

    async def __call__(self, command: CreatePaymentCommand) -> Payment:
        async with self._transaction_manager.start_transaction():
            existing_payment = await self._payment_gateway.get_by_idempotency_key(command.idempotency_key)
            if existing_payment is not None:
                return existing_payment

            created_at = datetime.now(UTC)
            payment = Payment(
                id=uuid4(),
                amount=command.amount,
                currency=command.currency,
                description=command.description,
                metadata=command.metadata,
                status=PaymentStatus.PENDING,
                idempotency_key=command.idempotency_key,
                webhook_url=command.webhook_url,
                created_at=created_at,
                processed_at=None,
            )
            outbox_message = OutboxMessage(
                id=uuid4(),
                event_name=PAYMENT_CREATED_EVENT,
                payload=PaymentCreatedEvent(payment_id=payment.id).model_dump(mode="json"),
                created_at=created_at,
                published_at=None,
            )

            await self._payment_gateway.add(payment)
            await self._outbox_gateway.add(outbox_message)
            await self._transaction_manager.commit()

            return payment
