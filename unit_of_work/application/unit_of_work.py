import abc

from types import TracebackType
from typing import TypeVar, Generic, Self

from unit_of_work.domain import AggregateRoot
from .event_publisher import EventPublisher
from .transaction import Transaction
from .repository import TransactionalRepository


T = TypeVar('T', bound=Transaction)


class UnitOfWork(abc.ABC, Generic[T]):
    def __init__(
            self,
            events_publisher: EventPublisher,
            tracked_repositories: list[TransactionalRepository[T]]
    ) -> None:
        self.__events_publisher = events_publisher
        self.__tracked_repositories = tracked_repositories
        self.__tracked_aggregate_roots: list[AggregateRoot] = []
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

        self.__transaction = None
        self.__publish_domain_events()

    @abc.abstractmethod
    async def _create_transaction(self) -> T:
        raise NotImplementedError

    def track_aggregate(self, aggregate: AggregateRoot) -> None:
        self.__tracked_aggregate_roots.append(aggregate)

    def __untrack_all_aggregates(self) -> None:
        self.__tracked_aggregate_roots.clear()

    def __publish_domain_events(self):
        for aggregate in self.__tracked_aggregate_roots:
            for event in aggregate.events:
                self.__events_publisher.publish(event)

            aggregate.clear_events()

        self.__untrack_all_aggregates()
