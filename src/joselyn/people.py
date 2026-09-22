from __future__ import annotations

from dataclasses import asdict, dataclass
from datetime import datetime, timezone
import json
from pathlib import Path
import sqlite3
from typing import Any
from uuid import uuid4

from .intake import IntakeBatch, IntakeRecord
from .models import Actor
from .runtime import HumanIntelligenceRuntime
from .security import AccessDenied, Principal


@dataclass(frozen=True, slots=True)
class ImportResult:
    created: int = 0
    updated: int = 0
    skipped: int = 0

    def to_dict(self) -> dict[str, int]:
        return asdict(self)


class PeopleStore:
    """Durable development registry with explicit authorization and history.

    SQLite remains a local development implementation. All public read/write
    operations are deny-by-default and require a Principal. Mutations append an
    immutable history row and may emit a correlated domain event.
    """

    _PROFILE_FIELDS = (
        "employee_id",
        "full_name",
        "email",
        "phone",
        "department",
        "position",
        "start_date",
        "status",
    )

    def __init__(
        self,
        path: str | Path,
        *,
        principal: Principal | None = None,
        runtime: HumanIntelligenceRuntime | None = None,
        tenant_id: str = "local",
    ) -> None:
        self.path = str(path)
        self.principal = principal
        self.runtime = runtime
        self.tenant_id = tenant_id
        self.connection = sqlite3.connect(self.path)
        self.connection.row_factory = sqlite3.Row
        self._ensure_schema()

    def close(self) -> None:
        self.connection.close()

    def __enter__(self) -> "PeopleStore":
        return self

    def __exit__(self, exc_type: object, exc: object, tb: object) -> None:
        self.close()

    def _require(self, permission: str) -> Principal:
        if self.principal is None:
            raise AccessDenied(
                f"no principal supplied; deny-by-default blocks {permission}"
            )
        self.principal.require(permission)
        return self.principal

    def _ensure_schema(self) -> None:
        self.connection.execute(
            """
            CREATE TABLE IF NOT EXISTS people (
                identity_key TEXT PRIMARY KEY,
                employee_id TEXT,
                full_name TEXT,
                email TEXT,
                phone TEXT,
                department TEXT,
                position TEXT,
                start_date TEXT,
                status TEXT,
                extra_json TEXT NOT NULL,
                provenance_json TEXT NOT NULL,
                source TEXT NOT NULL,
                updated_at TEXT NOT NULL
            )
            """
        )
        self.connection.execute(
            """
            CREATE TABLE IF NOT EXISTS people_history (
                history_id TEXT PRIMARY KEY,
                identity_key TEXT NOT NULL,
                operation TEXT NOT NULL,
                changed_fields_json TEXT NOT NULL,
                snapshot_json TEXT NOT NULL,
                source TEXT NOT NULL,
                actor_id TEXT NOT NULL,
                actor_role TEXT NOT NULL,
                correlation_id TEXT NOT NULL,
                event_id TEXT,
                occurred_at TEXT NOT NULL
            )
            """
        )
        self.connection.execute(
            "CREATE INDEX IF NOT EXISTS idx_people_employee_id ON people(employee_id)"
        )
        self.connection.execute(
            "CREATE INDEX IF NOT EXISTS idx_people_email ON people(email)"
        )
        self.connection.execute(
            "CREATE INDEX IF NOT EXISTS idx_people_name ON people(full_name)"
        )
        self.connection.execute(
            """
            CREATE INDEX IF NOT EXISTS idx_people_history_identity
            ON people_history(identity_key, occurred_at)
            """
        )
        self.connection.commit()

    @staticmethod
    def _value(record: IntakeRecord, key: str) -> str | None:
        value = record.data.get(key)
        if value is None:
            return None
        text = str(value).strip()
        return text or None

    @staticmethod
    def _decode_row(row: sqlite3.Row) -> dict[str, Any]:
        result = dict(row)
        result["extra_fields"] = json.loads(result.pop("extra_json"))
        result["provenance"] = json.loads(result.pop("provenance_json"))
        return result

    def _get_raw(self, identifier: str) -> dict[str, Any] | None:
        value = identifier.strip()
        row = self.connection.execute(
            """
            SELECT * FROM people
            WHERE identity_key = ? OR employee_id = ? OR lower(email) = lower(?)
            LIMIT 1
            """,
            (value, value, value),
        ).fetchone()
        return None if row is None else self._decode_row(row)

    @classmethod
    def _meaningful_snapshot(cls, record: dict[str, Any]) -> dict[str, Any]:
        return {
            **{key: record.get(key) for key in cls._PROFILE_FIELDS},
            "extra_fields": record.get("extra_fields", {}),
            "provenance": record.get("provenance", {}),
            "source": record.get("source"),
        }

    @classmethod
    def _changed_fields(
        cls,
        before: dict[str, Any] | None,
        after: dict[str, Any],
    ) -> list[str]:
        if before is None:
            fields = [
                key for key, value in cls._meaningful_snapshot(after).items()
                if value not in (None, "", {}, [])
            ]
            return sorted(fields)

        before_snapshot = cls._meaningful_snapshot(before)
        after_snapshot = cls._meaningful_snapshot(after)
        return sorted(
            key for key in after_snapshot
            if before_snapshot.get(key) != after_snapshot.get(key)
        )

    def _resolve_for_principal(
        self,
        identifier: str,
        principal: Principal,
    ) -> dict[str, Any] | None:
        value = identifier.strip()
        if principal.can("employee.read.contact"):
            return self._get_raw(value)

        row = self.connection.execute(
            """
            SELECT * FROM people
            WHERE employee_id = ?
               OR (identity_key = ? AND identity_key LIKE 'employee_id:%')
            LIMIT 1
            """,
            (value, value),
        ).fetchone()
        return None if row is None else self._decode_row(row)

    def _filter_record(self, record: dict[str, Any]) -> dict[str, Any]:
        principal = self._require("employee.read.basic")
        result = dict(record)

        if not principal.can("employee.read.contact"):
            result["email"] = "[restricted]" if result.get("email") else None
            result["phone"] = "[restricted]" if result.get("phone") else None
            identity = str(result.get("identity_key") or "")
            if identity.startswith("email:"):
                result["identity_key"] = "[restricted]"

        if not principal.can("employee.read.extra"):
            result["extra_fields"] = {}

        if not principal.can("employee.read.provenance"):
            result["provenance"] = {}
            result["source"] = "[restricted]"
        else:
            visible = set(self._PROFILE_FIELDS)
            if not principal.can("employee.read.contact"):
                visible -= {"email", "phone"}
            result["provenance"] = {
                key: value
                for key, value in result.get("provenance", {}).items()
                if key in visible
            }

        return result

    def upsert(
        self,
        record: IntakeRecord,
        *,
        source: str,
        correlation_id: str | None = None,
    ) -> str:
        principal = self._require("employee.update.profile")
        identity = record.identity_key()
        if identity is None:
            raise ValueError("record requires employee_id or email before persistence")

        before = self._get_raw(identity)
        now = datetime.now(timezone.utc).isoformat()
        correlation = correlation_id or str(uuid4())

        self.connection.execute(
            """
            INSERT INTO people (
                identity_key, employee_id, full_name, email, phone, department,
                position, start_date, status, extra_json, provenance_json, source,
                updated_at
            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            ON CONFLICT(identity_key) DO UPDATE SET
                employee_id = excluded.employee_id,
                full_name = excluded.full_name,
                email = excluded.email,
                phone = excluded.phone,
                department = excluded.department,
                position = excluded.position,
                start_date = excluded.start_date,
                status = excluded.status,
                extra_json = excluded.extra_json,
                provenance_json = excluded.provenance_json,
                source = excluded.source,
                updated_at = excluded.updated_at
            """,
            (
                identity,
                self._value(record, "employee_id"),
                self._value(record, "full_name"),
                self._value(record, "email"),
                self._value(record, "phone"),
                self._value(record, "department"),
                self._value(record, "position"),
                self._value(record, "start_date"),
                self._value(record, "status"),
                json.dumps(record.extra_fields, ensure_ascii=False, default=str),
                json.dumps(
                    {key: asdict(value) for key, value in record.provenance.items()},
                    ensure_ascii=False,
                    default=str,
                ),
                source,
                now,
            ),
        )

        after = self._get_raw(identity)
        assert after is not None
        changed_fields = self._changed_fields(before, after)

        if before is not None and not changed_fields:
            self.connection.rollback()
            return "skipped"

        operation = "created" if before is None else "updated"
        event_id: str | None = None
        if self.runtime is not None:
            event, _report = self.runtime.emit(
                f"employee.{operation}",
                actor=Actor(
                    type="integration" if principal.role == "Integration Service" else "user",
                    id=principal.id,
                ),
                tenant_id=self.tenant_id,
                payload={
                    "identity_key": identity,
                    "employee_id": after.get("employee_id"),
                    "changed_fields": changed_fields,
                },
                correlation_id=correlation,
            )
            event_id = event.event_id

        self.connection.execute(
            """
            INSERT INTO people_history (
                history_id, identity_key, operation, changed_fields_json,
                snapshot_json, source, actor_id, actor_role, correlation_id,
                event_id, occurred_at
            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """,
            (
                str(uuid4()),
                identity,
                operation,
                json.dumps(changed_fields, ensure_ascii=False),
                json.dumps(self._meaningful_snapshot(after), ensure_ascii=False, default=str),
                source,
                principal.id,
                principal.role,
                correlation,
                event_id,
                now,
            ),
        )
        self.connection.commit()
        return operation

    def import_batch(self, batch: IntakeBatch) -> ImportResult:
        self._require("employee.import")
        created = 0
        updated = 0
        skipped = 0
        for record in batch.records:
            if record.identity_key() is None:
                skipped += 1
                continue
            state = self.upsert(record, source=batch.source)
            if state == "created":
                created += 1
            elif state == "updated":
                updated += 1
            else:
                skipped += 1
        return ImportResult(created=created, updated=updated, skipped=skipped)

    def get(self, identifier: str) -> dict[str, Any] | None:
        principal = self._require("employee.read.basic")
        record = self._resolve_for_principal(identifier, principal)
        return None if record is None else self._filter_record(record)

    def list(
        self,
        *,
        query: str | None = None,
        limit: int = 50,
    ) -> list[dict[str, Any]]:
        self._require("employee.read.basic")
        safe_limit = max(1, min(limit, 500))
        principal = self.principal
        assert principal is not None
        if query and query.strip():
            like = f"%{query.strip()}%"
            if principal.can("employee.read.contact"):
                rows = self.connection.execute(
                    """
                    SELECT * FROM people
                    WHERE full_name LIKE ? OR email LIKE ? OR employee_id LIKE ?
                       OR department LIKE ? OR position LIKE ?
                    ORDER BY full_name COLLATE NOCASE, identity_key
                    LIMIT ?
                    """,
                    (like, like, like, like, like, safe_limit),
                ).fetchall()
            else:
                rows = self.connection.execute(
                    """
                    SELECT * FROM people
                    WHERE full_name LIKE ? OR employee_id LIKE ?
                       OR department LIKE ? OR position LIKE ?
                    ORDER BY full_name COLLATE NOCASE, identity_key
                    LIMIT ?
                    """,
                    (like, like, like, like, safe_limit),
                ).fetchall()
        else:
            rows = self.connection.execute(
                """
                SELECT * FROM people
                ORDER BY full_name COLLATE NOCASE, identity_key
                LIMIT ?
                """,
                (safe_limit,),
            ).fetchall()
        return [self._filter_record(self._decode_row(row)) for row in rows]

    def history(
        self,
        identifier: str,
        *,
        limit: int = 50,
    ) -> list[dict[str, Any]]:
        principal = self._require("employee.history.read")
        current = self._resolve_for_principal(identifier, principal)
        if current is None:
            return []

        safe_limit = max(1, min(limit, 500))
        rows = self.connection.execute(
            """
            SELECT * FROM people_history
            WHERE identity_key = ?
            ORDER BY occurred_at DESC, history_id DESC
            LIMIT ?
            """,
            (current["identity_key"], safe_limit),
        ).fetchall()

        result: list[dict[str, Any]] = []
        for row in rows:
            item = dict(row)
            item["changed_fields"] = json.loads(item.pop("changed_fields_json"))
            if (
                not principal.can("employee.read.contact")
                and str(item.get("identity_key") or "").startswith("email:")
            ):
                item["identity_key"] = "[restricted]"
            snapshot = json.loads(item.pop("snapshot_json"))
            item["snapshot"] = self._filter_record(snapshot)
            result.append(item)
        return result
