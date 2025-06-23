from asyncpg.transaction import Transaction as AsyncpgTransaction

from unit_of_work.application import Transaction


class AsyncpgTransactionAdapter(Transaction):
    def __init__(self, asyncpg_transaction: AsyncpgTransaction) -> None:
        self.__asyncpg_transaction = asyncpg_transaction

    async def commit(self) -> None:
        await self.__asyncpg_transaction.commit()

    async def rollback(self) -> None:
        await self.__asyncpg_transaction.rollback()
