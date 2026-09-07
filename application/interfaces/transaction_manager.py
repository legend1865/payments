from abc import ABC, abstractmethod
from contextlib import AbstractAsyncContextManager


class TransactionManager(ABC):
    @abstractmethod
    def start_transaction(self) -> AbstractAsyncContextManager[None]: ...

    @abstractmethod
    async def commit(self) -> None: ...

    @abstractmethod
    async def rollback(self) -> None: ...
