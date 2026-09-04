from collections.abc import AsyncIterator

from application.interactors import CreatePaymentInteractor, GetPaymentInteractor
from infrastructure.container import create_get_payment_interactor, create_payment_interactor

from fastapi import Depends, Request
from sqlalchemy.ext.asyncio import AsyncSession


async def get_session(request: Request) -> AsyncIterator[AsyncSession]:
    async with request.app.state.session_factory() as session:
        yield session


def get_create_payment_interactor(
    session: AsyncSession = Depends(get_session),
) -> CreatePaymentInteractor:
    return create_payment_interactor(session)


def get_get_payment_interactor(
    session: AsyncSession = Depends(get_session),
) -> GetPaymentInteractor:
    return create_get_payment_interactor(session)
