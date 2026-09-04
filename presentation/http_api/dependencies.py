from application.interactors import CreatePaymentInteractor, GetPaymentInteractor

from fastapi import Request


def get_create_payment_interactor(request: Request) -> CreatePaymentInteractor:
    return request.app.state.create_payment_interactor


def get_get_payment_interactor(request: Request) -> GetPaymentInteractor:
    return request.app.state.get_payment_interactor
