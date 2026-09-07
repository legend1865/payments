from collections.abc import AsyncIterator
from contextlib import asynccontextmanager

from application.interfaces import TransactionManager

from sqlalchemy.ext.asyncio import AsyncSession


class SQLAlchemyTransactionManager(TransactionManager):
    def __init__(self, session: AsyncSession) -> None:
        self._session = session

    @asynccontextmanager
    async def start_transaction(self) -> AsyncIterator[None]:
        async with self._session.begin():
            yield

    async def commit(self) -> None:
        await self._session.commit()

    async def rollback(self) -> None:
        await self._session.rollback()
