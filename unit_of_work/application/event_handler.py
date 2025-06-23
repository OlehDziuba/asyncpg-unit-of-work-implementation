import abc

from typing import TypeVar, Generic

from unit_of_work.domain import DomainEvent


T = TypeVar('T', bound=DomainEvent)


class EventHandler(abc.ABC, Generic[T]):
    @abc.abstractmethod
    async def handle(self, event: T) -> None:
        raise NotImplementedError
