import abc

from unit_of_work.domain import DomainEvent


class EventPublisher(abc.ABC):
    @abc.abstractmethod
    async def publish(self, event: DomainEvent) -> None:
        raise NotImplementedError
