from typing import Iterable, Mapping

from unit_of_work.application import EventHandler, EventPublisher
from unit_of_work.domain import DomainEvent


class EventsBus(EventPublisher):
    def __init__(
            self,
            handlers: Mapping[type[DomainEvent], Iterable[EventHandler[DomainEvent]]],
    ) -> None:
        self.__handlers = handlers

    async def publish(self, event: DomainEvent) -> None:
        for handler in self.__handlers.get(type(event), ()):
            await handler.publish(event)
