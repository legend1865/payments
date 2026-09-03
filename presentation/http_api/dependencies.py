from application.interfaces import PaymentService

from fastapi import Request


def get_payment_service(request: Request) -> PaymentService:
    return request.app.state.payment_service
