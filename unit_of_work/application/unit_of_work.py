import abc

from types import TracebackType
from typing import TypeVar, Generic, Self

from .transaction import Transaction
from .repository import TransactionalRepository


T = TypeVar('T', bound=Transaction)


class UnitOfWork(abc.ABC, Generic[T]):
    def __init__(self, tracked_repositories: list[TransactionalRepository[T]]):
        self.__tracked_repositories = tracked_repositories
        self.__transaction: T | None = None

    async def __aenter__(self) -> Self:
        self.__transaction = await self._create_transaction()

        for repository in self.__tracked_repositories:
            repository.set_new_transaction(self.__transaction)

        return self

    async def __aexit__(
            self,
            exc_type: type[Exception] | None,
            exc_val: Exception | None,
            exc_tb: TracebackType | None
    ) -> None:
        if exc_type:
            await self.__transaction.rollback()
        else:
            await self.__transaction.commit()

    @abc.abstractmethod
    async def _create_transaction(self) -> T:
        raise NotImplementedError
