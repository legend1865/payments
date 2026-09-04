from application.interactors import (
    CreatePaymentInteractor,
    GetPaymentInteractor,
    ProcessPaymentInteractor,
    PublishOutboxInteractor,
)
from application.interfaces import MessagePublisher, WebhookGateway
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


def create_publish_outbox_interactor(
    session: AsyncSession,
    message_publisher: MessagePublisher,
) -> PublishOutboxInteractor:
    return PublishOutboxInteractor(
        transaction_manager=SQLAlchemyTransactionManager(session),
        outbox_gateway=SQLAlchemyOutboxGateway(session),
        message_publisher=message_publisher,
    )


def create_process_payment_interactor(
    session: AsyncSession,
    webhook_gateway: WebhookGateway,
    success_probability: float,
    processing_delay: tuple[float, float],
) -> ProcessPaymentInteractor:
    return ProcessPaymentInteractor(
        transaction_manager=SQLAlchemyTransactionManager(session),
        payment_gateway=SQLAlchemyPaymentGateway(session),
        webhook_gateway=webhook_gateway,
        success_probability=success_probability,
        processing_delay=processing_delay,
    )
