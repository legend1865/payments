from uuid import UUID

from application.dto import (
    CreatePaymentCommand,
    CreatePaymentRequest,
    CreatePaymentResponse,
    PaymentResponse,
)
from application.exceptions import PaymentNotFoundError
from application.interactors import CreatePaymentInteractor, GetPaymentInteractor
from presentation.http_api.dependencies import (
    get_create_payment_interactor,
    get_get_payment_interactor,
)

from fastapi import APIRouter, Depends, Header, HTTPException, status


router = APIRouter(prefix="/api/v1/payments", tags=["payments"])


@router.post("", status_code=status.HTTP_202_ACCEPTED)
async def create_payment(
    payload: CreatePaymentRequest,
    idempotency_key: str = Header(alias="Idempotency-Key"),
    interactor: CreatePaymentInteractor = Depends(get_create_payment_interactor),
) -> CreatePaymentResponse:
    payment = await interactor(
        CreatePaymentCommand(
            amount=payload.amount,
            currency=payload.currency,
            description=payload.description,
            metadata=payload.metadata,
            webhook_url=str(payload.webhook_url),
            idempotency_key=idempotency_key,
        )
    )
    return CreatePaymentResponse(
        payment_id=payment.id,
        status=payment.status,
        created_at=payment.created_at,
    )


@router.get("/{payment_id}")
async def get_payment(
    payment_id: UUID,
    interactor: GetPaymentInteractor = Depends(get_get_payment_interactor),
) -> PaymentResponse:
    try:
        payment = await interactor(payment_id)
    except PaymentNotFoundError as error:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Payment not found") from error

    return PaymentResponse(
        payment_id=payment.id,
        amount=payment.amount,
        currency=payment.currency,
        description=payment.description,
        metadata=payment.metadata,
        status=payment.status,
        idempotency_key=payment.idempotency_key,
        webhook_url=payment.webhook_url,
        created_at=payment.created_at,
        processed_at=payment.processed_at,
    )
