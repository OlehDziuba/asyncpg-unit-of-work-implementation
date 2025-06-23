import dataclasses
from datetime import datetime, UTC
from uuid import UUID


@dataclasses.dataclass(frozen=True)
class DomainEvent:
    occurred_at: datetime


class Entity:
    def __init__(self):
        self.__domain_events: list[DomainEvent] = []

    def _registrate_event(self, event: DomainEvent) -> None:
        self.__domain_events.append(event)

    def clear_events(self) -> None:
        self.__domain_events.clear()

    @property
    def events(self) -> list[DomainEvent]:
        return self.__domain_events
