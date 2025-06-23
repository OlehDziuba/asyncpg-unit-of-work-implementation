from typing import TypeVar, Generic

from .transaction import Transaction


T = TypeVar('T', bound=Transaction)


class TransactionalRepository(Generic[T]):
    def __init__(self):
        self._transaction: T | None = None

    def set_new_transaction(self, transaction: T) -> None:
        self._transaction = transaction
