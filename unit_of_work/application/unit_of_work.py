import abc

from types import TracebackType
from typing import TypeVar, Generic, Self

from unit_of_work.domain import Entity
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
        self.__tracked_entities: list[Entity] = []
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

    def track_entity(self, entity: Entity) -> None:
        self.__tracked_entities.append(entity)

    def __untrack_all_entities(self) -> None:
        self.__tracked_entities.clear()

    def __publish_domain_events(self):
        for entity in self.__tracked_entities:
            for event in entity.events:
                self.__events_publisher.publish(event)

            entity.clear_events()

        self.__untrack_all_entities()
