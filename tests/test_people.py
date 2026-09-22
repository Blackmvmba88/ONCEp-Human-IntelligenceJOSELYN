from pathlib import Path
import tempfile
import unittest

from joselyn.intake import IntakeBatch, normalize_row
from joselyn.people import PeopleStore


class PeopleStoreTests(unittest.TestCase):
    def test_import_list_show_and_update(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            db = Path(tmp) / "joselyn.db"
            first = normalize_row(
                {
                    "id empleado": "EMP-9",
                    "nombre": "Mara Lopez",
                    "correo": "mara@example.com",
                    "puesto": "Recruiter",
                    "departamento": "People",
                },
                source="people.csv",
                row_number=2,
            )
            batch = IntakeBatch(source="people.csv", source_format="csv", records=[first])

            with PeopleStore(db) as store:
                result = store.import_batch(batch)
                self.assertEqual(result.created, 1)
                self.assertEqual(store.get("EMP-9")["full_name"], "Mara Lopez")
                self.assertEqual(len(store.list(query="Recruiter")), 1)

                updated = normalize_row(
                    {
                        "id empleado": "EMP-9",
                        "nombre": "Mara Lopez",
                        "correo": "mara@example.com",
                        "puesto": "Senior Recruiter",
                        "departamento": "People",
                    },
                    source="people-v2.csv",
                    row_number=2,
                )
                result2 = store.import_batch(
                    IntakeBatch(source="people-v2.csv", source_format="csv", records=[updated])
                )
                self.assertEqual(result2.updated, 1)
                self.assertEqual(store.get("mara@example.com")["position"], "Senior Recruiter")

    def test_record_without_stable_identity_is_skipped(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            db = Path(tmp) / "joselyn.db"
            record = normalize_row({"nombre": "No Identity"}, source="x", row_number=1)
            with PeopleStore(db) as store:
                result = store.import_batch(
                    IntakeBatch(source="x", source_format="json", records=[record])
                )
            self.assertEqual(result.skipped, 1)


if __name__ == "__main__":
    unittest.main()
