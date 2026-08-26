from __future__ import annotations

from dataclasses import asdict, dataclass
from datetime import datetime, timezone
from typing import Any
from uuid import uuid4

from .event_bus import DeliveryReport, InMemoryEventBus
from .models import Actor, DomainEvent


@dataclass(frozen=True, slots=True)
class AuditRecord:
    id: str
    action: str
    resource_type: str
    resource_id: str
    occurred_at: str
    correlation_id: str
    actor_type: str
    actor_id: str
    summary: str

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)


class HumanIntelligenceRuntime:
    """Bootstrap execution core for PONCE.

    The runtime emits validated domain facts, routes them through the event bus,
    and records an audit trace whether delivery succeeds or fails.
    """

    def __init__(self, bus: InMemoryEventBus | None = None) -> None:
        self.bus = bus or InMemoryEventBus()
        self.audit_log: list[AuditRecord] = []

    def emit(
        self,
        event_type: str,
        *,
        actor: Actor,
        tenant_id: str,
        payload: dict[str, Any] | None = None,
        event_version: int = 1,
        correlation_id: str | None = None,
        causation_id: str | None = None,
    ) -> tuple[DomainEvent, DeliveryReport]:
        event = DomainEvent.create(
            event_type,
            actor=actor,
            tenant_id=tenant_id,
            payload=payload,
            event_version=event_version,
            correlation_id=correlation_id,
            causation_id=causation_id,
        )
        report = self.bus.publish(event)
        self.audit_log.append(self._audit(event, report))
        return event, report

    def _audit(self, event: DomainEvent, report: DeliveryReport) -> AuditRecord:
        state = "delivered" if report.ok else "delivery_failed"
        summary = (
            f"{event.event_type} {state}; "
            f"delivered={len(report.delivered)} "
            f"skipped={len(report.skipped)} failed={len(report.failed)}"
        )
        return AuditRecord(
            id=str(uuid4()),
            action="domain_event.publish",
            resource_type="DomainEvent",
            resource_id=event.event_id,
            occurred_at=datetime.now(timezone.utc).isoformat(),
            correlation_id=event.correlation_id,
            actor_type=event.actor.type,
            actor_id=event.actor.id,
            summary=summary,
        )

    def status(self) -> dict[str, Any]:
        return {
            "platform": "PONCE",
            "interface": "JOSELYN CLI",
            "runtime": "bootstrap",
            "audit_records": len(self.audit_log),
            "event_bus": "in-memory",
        }
