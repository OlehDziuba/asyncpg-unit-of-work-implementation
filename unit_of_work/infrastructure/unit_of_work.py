from types import TracebackType

from asyncpg import Pool, Connection

from unit_of_work.application import EventPublisher, TransactionalRepository, UnitOfWork
from .transaction_adapter import AsyncpgTransactionAdapter


class AsyncpgUnitOfWork(UnitOfWork[AsyncpgTransactionAdapter]):
    def __init__(
            self,
            pool: Pool,
            events_publisher: EventPublisher,
            tracked_repositories: list[TransactionalRepository[AsyncpgTransactionAdapter]],
    ) -> None:
        super().__init__(events_publisher, tracked_repositories)
        self.__pool = pool
        self.__connection: Connection | None = None

    async def _create_transaction(self) -> AsyncpgTransactionAdapter:
        self.__connection = await self.__pool.acquire()
        asyncpg_transaction = self.__connection.transaction()
        await asyncpg_transaction.start()

        return AsyncpgTransactionAdapter(asyncpg_transaction)

    async def __aexit__(
            self,
            exc_type: type[Exception] | None,
            exc_val: Exception | None,
            exc_tb: TracebackType | None
    ) -> None:
        try:
            await super().__aexit__(exc_type, exc_val, exc_tb)
        finally:
            await self.__pool.release(self.__connection)
            self.__connection = None
