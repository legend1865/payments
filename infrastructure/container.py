from application.interactors import CreatePaymentInteractor, GetPaymentInteractor
from infrastructure.database import (
    SQLAlchemyOutboxGateway,
    SQLAlchemyPaymentGateway,
    SQLAlchemyTransactionManager,
)

from sqlalchemy.ext.asyncio import AsyncSession


def create_payment_interactor(session: AsyncSession) -> CreatePaymentInteractor:
    payment_gateway = SQLAlchemyPaymentGateway(session)
    outbox_gateway = SQLAlchemyOutboxGateway(session)
    transaction_manager = SQLAlchemyTransactionManager(session)

    return CreatePaymentInteractor(
        transaction_manager=transaction_manager,
        payment_gateway=payment_gateway,
        outbox_gateway=outbox_gateway,
    )


def create_get_payment_interactor(session: AsyncSession) -> GetPaymentInteractor:
    return GetPaymentInteractor(payment_gateway=SQLAlchemyPaymentGateway(session))
