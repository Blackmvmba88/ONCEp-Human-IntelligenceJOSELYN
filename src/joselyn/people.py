from __future__ import annotations

from dataclasses import asdict, dataclass
from datetime import datetime, timezone
import json
from pathlib import Path
import sqlite3
from typing import Any

from .intake import IntakeBatch, IntakeRecord


@dataclass(frozen=True, slots=True)
class ImportResult:
    created: int = 0
    updated: int = 0
    skipped: int = 0

    def to_dict(self) -> dict[str, int]:
        return asdict(self)


class PeopleStore:
    """Small durable registry for the first People Core vertical slice.

    This local SQLite implementation is a development repository, not the final
    enterprise persistence decision. It makes list -> detail -> source trace
    executable while keeping the storage boundary explicit.
    """

    def __init__(self, path: str | Path) -> None:
        self.path = str(path)
        self.connection = sqlite3.connect(self.path)
        self.connection.row_factory = sqlite3.Row
        self._ensure_schema()

    def close(self) -> None:
        self.connection.close()

    def __enter__(self) -> "PeopleStore":
        return self

    def __exit__(self, exc_type: object, exc: object, tb: object) -> None:
        self.close()

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
            "CREATE INDEX IF NOT EXISTS idx_people_employee_id ON people(employee_id)"
        )
        self.connection.execute(
            "CREATE INDEX IF NOT EXISTS idx_people_email ON people(email)"
        )
        self.connection.execute(
            "CREATE INDEX IF NOT EXISTS idx_people_name ON people(full_name)"
        )
        self.connection.commit()

    @staticmethod
    def _value(record: IntakeRecord, key: str) -> str | None:
        value = record.data.get(key)
        if value is None:
            return None
        text = str(value).strip()
        return text or None

    def upsert(self, record: IntakeRecord, *, source: str) -> str:
        identity = record.identity_key()
        if identity is None:
            raise ValueError("record requires employee_id or email before persistence")

        existed = self.connection.execute(
            "SELECT 1 FROM people WHERE identity_key = ?", (identity,)
        ).fetchone() is not None

        now = datetime.now(timezone.utc).isoformat()
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
        self.connection.commit()
        return "updated" if existed else "created"

    def import_batch(self, batch: IntakeBatch) -> ImportResult:
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
            else:
                updated += 1
        return ImportResult(created=created, updated=updated, skipped=skipped)

    @staticmethod
    def _row_to_dict(row: sqlite3.Row) -> dict[str, Any]:
        result = dict(row)
        result["extra_fields"] = json.loads(result.pop("extra_json"))
        result["provenance"] = json.loads(result.pop("provenance_json"))
        return result

    def get(self, identifier: str) -> dict[str, Any] | None:
        value = identifier.strip()
        row = self.connection.execute(
            """
            SELECT * FROM people
            WHERE identity_key = ? OR employee_id = ? OR lower(email) = lower(?)
            LIMIT 1
            """,
            (value, value, value),
        ).fetchone()
        return None if row is None else self._row_to_dict(row)

    def list(self, *, query: str | None = None, limit: int = 50) -> list[dict[str, Any]]:
        safe_limit = max(1, min(limit, 500))
        if query and query.strip():
            like = f"%{query.strip()}%"
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
                ORDER BY full_name COLLATE NOCASE, identity_key
                LIMIT ?
                """,
                (safe_limit,),
            ).fetchall()
        return [self._row_to_dict(row) for row in rows]
