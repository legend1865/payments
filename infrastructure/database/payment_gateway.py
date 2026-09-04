from uuid import UUID

from application.dto import Currency, Payment, PaymentStatus
from infrastructure.database.models import PaymentModel

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession


class SQLAlchemyPaymentGateway:
    def __init__(self, session: AsyncSession) -> None:
        self._session = session

    async def add(self, payment: Payment) -> None:
        self._session.add(
            PaymentModel(
                id=payment.id,
                amount=payment.amount,
                currency=payment.currency.value,
                description=payment.description,
                metadata_=payment.metadata,
                status=payment.status.value,
                idempotency_key=payment.idempotency_key,
                webhook_url=payment.webhook_url,
                created_at=payment.created_at,
                processed_at=payment.processed_at,
            )
        )

    async def get_by_id(self, payment_id: UUID) -> Payment | None:
        model = await self._session.get(PaymentModel, payment_id)
        return self._to_dto(model) if model is not None else None

    async def get_by_idempotency_key(self, idempotency_key: str) -> Payment | None:
        statement = select(PaymentModel).where(PaymentModel.idempotency_key == idempotency_key)
        model = await self._session.scalar(statement)
        return self._to_dto(model) if model is not None else None

    @staticmethod
    def _to_dto(model: PaymentModel) -> Payment:
        return Payment(
            id=model.id,
            amount=model.amount,
            currency=Currency(model.currency),
            description=model.description,
            metadata=model.metadata_,
            status=PaymentStatus(model.status),
            idempotency_key=model.idempotency_key,
            webhook_url=model.webhook_url,
            created_at=model.created_at,
            processed_at=model.processed_at,
        )
