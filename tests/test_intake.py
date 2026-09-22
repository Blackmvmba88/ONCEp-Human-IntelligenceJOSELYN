import json
from pathlib import Path
import tempfile
import unittest

from joselyn.intake import load_path, normalize_row


class IntakeTests(unittest.TestCase):
    def test_spanish_headers_map_to_canonical_fields(self) -> None:
        record = normalize_row(
            {
                "ID Empleado": "EMP-7",
                "Nombre Completo": "Ana Ruiz",
                "Correo": "ana@example.com",
                "Departamento": "People",
                "Dato local": "preserve-me",
            },
            source="memory",
            row_number=2,
        )

        self.assertEqual(record.data["employee_id"], "EMP-7")
        self.assertEqual(record.data["full_name"], "Ana Ruiz")
        self.assertEqual(record.data["email"], "ana@example.com")
        self.assertEqual(record.data["department"], "People")
        self.assertEqual(record.extra_fields["Dato local"], "preserve-me")
        self.assertEqual(record.provenance["email"].original_field, "Correo")

    def test_csv_detects_duplicate_employee_identity(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            path = Path(tmp) / "people.csv"
            path.write_text(
                "id empleado,nombre,correo\n"
                "EMP-1,Ana,ana@example.com\n"
                "EMP-1,Ana Ruiz,ana@example.com\n",
                encoding="utf-8",
            )
            batch = load_path(path)

        self.assertEqual(len(batch.records), 2)
        self.assertEqual(batch.duplicate_keys, ["employee_id:emp-1"])

    def test_json_array_uses_same_intake_contract(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            path = Path(tmp) / "people.json"
            path.write_text(
                json.dumps([{"nombre": "Luis", "correo": "luis@example.com"}]),
                encoding="utf-8",
            )
            batch = load_path(path)

        self.assertEqual(batch.source_format, "json")
        self.assertEqual(batch.records[0].data["full_name"], "Luis")
        self.assertEqual(batch.records[0].identity_key(), "email:luis@example.com")

    def test_missing_identity_is_visible(self) -> None:
        record = normalize_row({"nombre": "Sin ID"}, source="memory", row_number=1)
        self.assertTrue(any("stable" in warning for warning in record.warnings))


if __name__ == "__main__":
    unittest.main()
