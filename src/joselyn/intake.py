from __future__ import annotations

from dataclasses import asdict, dataclass, field
import csv
import json
from pathlib import Path
import re
from typing import Any


_CANONICAL_FIELDS: dict[str, tuple[str, ...]] = {
    "employee_id": (
        "employee_id", "employee id", "id empleado", "id_empleado",
        "numero empleado", "numero_empleado", "no empleado", "no_empleado",
    ),
    "full_name": (
        "full_name", "full name", "nombre", "nombre completo",
        "nombre_completo", "empleado",
    ),
    "email": ("email", "e-mail", "correo", "correo electronico", "correo_electronico"),
    "phone": ("phone", "telefono", "tel", "movil", "celular"),
    "department": ("department", "departamento", "area", "área"),
    "position": ("position", "puesto", "cargo", "job title", "job_title"),
    "start_date": (
        "start_date", "start date", "fecha ingreso", "fecha_ingreso",
        "fecha de ingreso", "hire date", "hire_date",
    ),
    "status": ("status", "estado", "estatus", "employment status", "employment_status"),
}


def _key(value: str) -> str:
    value = value.strip().lower()
    value = re.sub(r"[\s\-]+", "_", value)
    return value


_ALIAS_TO_CANONICAL: dict[str, str] = {}
for canonical, aliases in _CANONICAL_FIELDS.items():
    _ALIAS_TO_CANONICAL[_key(canonical)] = canonical
    for alias in aliases:
        _ALIAS_TO_CANONICAL[_key(alias)] = canonical


@dataclass(frozen=True, slots=True)
class FormatCapability:
    name: str
    extensions: tuple[str, ...]
    status: str
    notes: str

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)


@dataclass(frozen=True, slots=True)
class FieldProvenance:
    source: str
    row_number: int | None
    original_field: str | None


@dataclass(slots=True)
class IntakeRecord:
    data: dict[str, Any]
    extra_fields: dict[str, Any]
    provenance: dict[str, FieldProvenance]
    warnings: list[str] = field(default_factory=list)

    def identity_key(self) -> str | None:
        employee_id = str(self.data.get("employee_id") or "").strip().lower()
        email = str(self.data.get("email") or "").strip().lower()
        if employee_id:
            return f"employee_id:{employee_id}"
        if email:
            return f"email:{email}"
        return None

    def to_dict(self) -> dict[str, Any]:
        return {
            "data": dict(self.data),
            "extra_fields": dict(self.extra_fields),
            "provenance": {key: asdict(value) for key, value in self.provenance.items()},
            "warnings": list(self.warnings),
        }


@dataclass(slots=True)
class IntakeBatch:
    source: str
    source_format: str
    records: list[IntakeRecord]
    duplicate_keys: list[str] = field(default_factory=list)

    def to_dict(self) -> dict[str, Any]:
        return {
            "source": self.source,
            "source_format": self.source_format,
            "record_count": len(self.records),
            "duplicate_keys": list(self.duplicate_keys),
            "records": [record.to_dict() for record in self.records],
        }


FORMAT_CAPABILITIES: tuple[FormatCapability, ...] = (
    FormatCapability("CSV", (".csv",), "implemented", "Header mapping, normalization and duplicate detection."),
    FormatCapability("TSV", (".tsv",), "implemented", "Tab-delimited records use the same normalized intake contract."),
    FormatCapability("JSON", (".json",), "implemented", "Object or array-of-object ingestion."),
    FormatCapability("Excel", (".xlsx", ".xls"), "adapter-planned", "Will map sheets into the same intake contract."),
    FormatCapability("PDF", (".pdf",), "adapter-planned", "Document extraction must preserve page and field provenance."),
    FormatCapability("Image", (".png", ".jpg", ".jpeg", ".heic"), "adapter-planned", "Vision/OCR adapter feeds proposed fields for human validation."),
    FormatCapability("Audio", (".wav", ".mp3", ".m4a", ".ogg"), "adapter-planned", "Speech adapter feeds structured dictation into the same contract."),
)


def capabilities() -> list[dict[str, Any]]:
    return [item.to_dict() for item in FORMAT_CAPABILITIES]


def normalize_row(row: dict[str, Any], *, source: str, row_number: int | None) -> IntakeRecord:
    data: dict[str, Any] = {}
    extra: dict[str, Any] = {}
    provenance: dict[str, FieldProvenance] = {}

    for raw_field, value in row.items():
        field_name = str(raw_field)
        canonical = _ALIAS_TO_CANONICAL.get(_key(field_name))
        if canonical:
            data[canonical] = value
            provenance[canonical] = FieldProvenance(source, row_number, field_name)
        else:
            extra[field_name] = value

    warnings: list[str] = []
    if not data.get("employee_id") and not data.get("email"):
        warnings.append("record has no stable employee_id or email identity")
    if not data.get("full_name"):
        warnings.append("record has no full_name")

    return IntakeRecord(data=data, extra_fields=extra, provenance=provenance, warnings=warnings)


def _deduplicate(records: list[IntakeRecord]) -> list[str]:
    seen: set[str] = set()
    duplicates: set[str] = set()
    for record in records:
        identity = record.identity_key()
        if identity is None:
            continue
        if identity in seen:
            duplicates.add(identity)
        seen.add(identity)
    return sorted(duplicates)


def _load_delimited(path: Path, *, delimiter: str) -> IntakeBatch:
    with path.open("r", encoding="utf-8-sig", newline="") as handle:
        reader = csv.DictReader(handle, delimiter=delimiter)
        records = [
            normalize_row(dict(row), source=str(path), row_number=index)
            for index, row in enumerate(reader, start=2)
        ]
    return IntakeBatch(
        source=str(path),
        source_format="tsv" if delimiter == "\t" else "csv",
        records=records,
        duplicate_keys=_deduplicate(records),
    )


def _load_json(path: Path) -> IntakeBatch:
    with path.open("r", encoding="utf-8-sig") as handle:
        payload = json.load(handle)

    if isinstance(payload, dict):
        rows = [payload]
    elif isinstance(payload, list) and all(isinstance(item, dict) for item in payload):
        rows = payload
    else:
        raise ValueError("JSON intake must be an object or an array of objects")

    records = [
        normalize_row(dict(row), source=str(path), row_number=index)
        for index, row in enumerate(rows, start=1)
    ]
    return IntakeBatch(
        source=str(path),
        source_format="json",
        records=records,
        duplicate_keys=_deduplicate(records),
    )


def load_path(path_value: str | Path) -> IntakeBatch:
    path = Path(path_value)
    if not path.exists():
        raise FileNotFoundError(path)

    suffix = path.suffix.lower()
    if suffix == ".csv":
        return _load_delimited(path, delimiter=",")
    if suffix == ".tsv":
        return _load_delimited(path, delimiter="\t")
    if suffix == ".json":
        return _load_json(path)

    known = ", ".join(ext for item in FORMAT_CAPABILITIES for ext in item.extensions)
    raise ValueError(f"unsupported intake format {suffix!r}; known formats: {known}")
