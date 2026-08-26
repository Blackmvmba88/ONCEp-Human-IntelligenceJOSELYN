from __future__ import annotations

from dataclasses import dataclass, field
from typing import Callable

from .models import DomainEvent

EventHandler = Callable[[DomainEvent], None]


@dataclass(slots=True)
class DeliveryFailure:
    handler: str
    error: str


@dataclass(slots=True)
class DeliveryReport:
    event_id: str
    delivered: list[str] = field(default_factory=list)
    skipped: list[str] = field(default_factory=list)
    failed: list[DeliveryFailure] = field(default_factory=list)

    @property
    def ok(self) -> bool:
        return not self.failed


class InMemoryEventBus:
    """Deterministic bootstrap bus for local development and contract tests.

    This is intentionally not the production message broker. It establishes
    handler registration, per-handler idempotency and visible delivery failures.
    """

    def __init__(self) -> None:
        self._handlers: dict[str, list[EventHandler]] = {}
        self._processed: set[tuple[str, str]] = set()

    def subscribe(self, event_type: str, handler: EventHandler) -> None:
        self._handlers.setdefault(event_type, []).append(handler)

    def publish(self, event: DomainEvent) -> DeliveryReport:
        report = DeliveryReport(event_id=event.event_id)

        for handler in self._handlers.get(event.event_type, []):
            name = self._handler_name(handler)
            key = (event.event_id, name)

            if key in self._processed:
                report.skipped.append(name)
                continue

            try:
                handler(event)
            except Exception as exc:  # boundary: failures must become visible
                report.failed.append(
                    DeliveryFailure(handler=name, error=f"{type(exc).__name__}: {exc}")
                )
                continue

            self._processed.add(key)
            report.delivered.append(name)

        return report

    @staticmethod
    def _handler_name(handler: EventHandler) -> str:
        module = getattr(handler, "__module__", "unknown")
        qualname = getattr(handler, "__qualname__", repr(handler))
        return f"{module}.{qualname}"
