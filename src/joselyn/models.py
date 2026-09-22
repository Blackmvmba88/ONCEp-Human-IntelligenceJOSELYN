from __future__ import annotations

from dataclasses import asdict, dataclass, field
from datetime import datetime, timezone
import re
from typing import Any
from uuid import uuid4

_EVENT_TYPE = re.compile(r"^[a-z][a-z0-9_]*\.[a-z][a-z0-9_]*$")


@dataclass(frozen=True, slots=True)
class Actor:
    type: str
    id: str

    def __post_init__(self) -> None:
        if self.type not in {"user", "system", "integration"}:
            raise ValueError("actor.type must be user, system, or integration")
        if not self.id.strip():
            raise ValueError("actor.id is required")


@dataclass(frozen=True, slots=True)
class DomainEvent:
    event_id: str
    event_type: str
    event_version: int
    occurred_at: str
    actor: Actor
    tenant_id: str
    correlation_id: str
    causation_id: str | None = None
    payload: dict[str, Any] = field(default_factory=dict)

    def __post_init__(self) -> None:
        if not _EVENT_TYPE.match(self.event_type):
            raise ValueError("event_type must match <entity>.<fact>")
        if self.event_version < 1:
            raise ValueError("event_version must be >= 1")
        if not self.tenant_id.strip():
            raise ValueError("tenant_id is required")
        if not self.correlation_id.strip():
            raise ValueError("correlation_id is required")

    @classmethod
    def create(
        cls,
        event_type: str,
        *,
        actor: Actor,
        tenant_id: str,
        payload: dict[str, Any] | None = None,
        event_version: int = 1,
        correlation_id: str | None = None,
        causation_id: str | None = None,
    ) -> "DomainEvent":
        return cls(
            event_id=str(uuid4()),
            event_type=event_type,
            event_version=event_version,
            occurred_at=datetime.now(timezone.utc).isoformat(),
            actor=actor,
            tenant_id=tenant_id,
            correlation_id=correlation_id or str(uuid4()),
            causation_id=causation_id,
            payload=payload or {},
        )

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)
