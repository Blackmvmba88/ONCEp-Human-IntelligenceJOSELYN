from pathlib import Path
import tempfile
import unittest

from joselyn.intake import IntakeBatch, normalize_row
from joselyn.people import PeopleStore
from joselyn.runtime import HumanIntelligenceRuntime
from joselyn.security import AccessDenied, Principal


class PeopleStoreTests(unittest.TestCase):
    def _record(self, *, position: str = "Recruiter"):
        return normalize_row(
            {
                "id empleado": "EMP-9",
                "nombre": "Mara Lopez",
                "correo": "mara@example.com",
                "telefono": "555-0101",
                "puesto": position,
                "departamento": "People",
                "Dato local": "preserve-me",
            },
            source="people.csv",
            row_number=2,
        )

    def test_import_list_show_and_update(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            db = Path(tmp) / "joselyn.db"
            principal = Principal(id="HR-1", role="HR Manager")
            first = self._record()
            batch = IntakeBatch(source="people.csv", source_format="csv", records=[first])

            with PeopleStore(db, principal=principal) as store:
                result = store.import_batch(batch)
                self.assertEqual(result.created, 1)
                self.assertEqual(store.get("EMP-9")["full_name"], "Mara Lopez")
                self.assertEqual(len(store.list(query="Recruiter")), 1)

                updated = self._record(position="Senior Recruiter")
                result2 = store.import_batch(
                    IntakeBatch(source="people-v2.csv", source_format="csv", records=[updated])
                )
                self.assertEqual(result2.updated, 1)
                self.assertEqual(store.get("mara@example.com")["position"], "Senior Recruiter")
                self.assertEqual(len(store.history("EMP-9")), 2)

    def test_record_without_stable_identity_is_skipped(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            db = Path(tmp) / "joselyn.db"
            record = normalize_row({"nombre": "No Identity"}, source="x", row_number=1)
            principal = Principal(id="HR-1", role="HR Manager")
            with PeopleStore(db, principal=principal) as store:
                result = store.import_batch(
                    IntakeBatch(source="x", source_format="json", records=[record])
                )
            self.assertEqual(result.skipped, 1)

    def test_deny_by_default_blocks_reads_and_mutations(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            db = Path(tmp) / "joselyn.db"
            store = PeopleStore(db)
            with self.assertRaises(AccessDenied):
                store.list()
            with self.assertRaises(AccessDenied):
                store.import_batch(
                    IntakeBatch(
                        source="people.csv",
                        source_format="csv",
                        records=[self._record()],
                    )
                )
            store.close()

    def test_hr_manager_import_appends_history_and_correlated_event(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            db = Path(tmp) / "joselyn.db"
            runtime = HumanIntelligenceRuntime()
            principal = Principal(id="USER-1", role="HR Manager")

            with PeopleStore(db, principal=principal, runtime=runtime) as store:
                first = store.import_batch(
                    IntakeBatch(
                        source="people.csv",
                        source_format="csv",
                        records=[self._record()],
                    )
                )
                second = store.import_batch(
                    IntakeBatch(
                        source="people-v2.csv",
                        source_format="csv",
                        records=[self._record(position="Senior Recruiter")],
                    )
                )
                history = store.history("EMP-9")

            self.assertEqual(first.created, 1)
            self.assertEqual(second.updated, 1)
            self.assertEqual(len(history), 2)
            self.assertEqual(history[0]["operation"], "updated")
            self.assertIn("position", history[0]["changed_fields"])
            self.assertEqual(len(runtime.audit_log), 2)
            self.assertEqual(
                history[0]["correlation_id"],
                runtime.audit_log[-1].correlation_id,
            )
            self.assertEqual(history[0]["event_id"], runtime.audit_log[-1].resource_id)

    def test_manager_get_masks_contact_extra_and_provenance(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            db = Path(tmp) / "joselyn.db"
            hr = Principal(id="HR-1", role="HR Manager")
            with PeopleStore(db, principal=hr) as store:
                store.import_batch(
                    IntakeBatch(
                        source="people.csv",
                        source_format="csv",
                        records=[self._record()],
                    )
                )

            manager = Principal(id="MGR-1", role="Manager")
            with PeopleStore(db, principal=manager) as store:
                record = store.get("EMP-9")

            assert record is not None
            self.assertEqual(record["email"], "[restricted]")
            self.assertEqual(record["phone"], "[restricted]")
            self.assertEqual(record["extra_fields"], {})
            self.assertEqual(record["provenance"], {})
            self.assertEqual(record["source"], "[restricted]")
            self.assertEqual(record["full_name"], "Mara Lopez")

    def test_recruiter_can_read_contact_but_not_extra_or_provenance(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            db = Path(tmp) / "joselyn.db"
            hr = Principal(id="HR-1", role="HR Manager")
            with PeopleStore(db, principal=hr) as store:
                store.import_batch(
                    IntakeBatch(
                        source="people.csv",
                        source_format="csv",
                        records=[self._record()],
                    )
                )

            recruiter = Principal(id="REC-1", role="Recruiter")
            with PeopleStore(db, principal=recruiter) as store:
                record = store.get("EMP-9")
                with self.assertRaises(AccessDenied):
                    store.history("EMP-9")

            assert record is not None
            self.assertEqual(record["email"], "mara@example.com")
            self.assertEqual(record["extra_fields"], {})
            self.assertEqual(record["source"], "[restricted]")

    def test_unchanged_reimport_is_skipped_without_new_history(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            db = Path(tmp) / "joselyn.db"
            hr = Principal(id="HR-1", role="HR Manager")
            batch = IntakeBatch(
                source="people.csv",
                source_format="csv",
                records=[self._record()],
            )
            with PeopleStore(db, principal=hr) as store:
                first = store.import_batch(batch)
                second = store.import_batch(batch)
                history = store.history("EMP-9")

            self.assertEqual(first.created, 1)
            self.assertEqual(second.skipped, 1)
            self.assertEqual(len(history), 1)

    def test_manager_cannot_probe_contact_identity_by_email(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            db = Path(tmp) / "joselyn.db"
            hr = Principal(id="HR-1", role="HR Manager")
            with PeopleStore(db, principal=hr) as store:
                store.import_batch(
                    IntakeBatch(
                        source="people.csv",
                        source_format="csv",
                        records=[self._record()],
                    )
                )

            manager = Principal(id="MGR-1", role="Manager")
            with PeopleStore(db, principal=manager) as store:
                self.assertIsNone(store.get("mara@example.com"))
                self.assertEqual(store.list(query="mara@example.com"), [])

    def test_auditor_cannot_probe_history_by_contact_identity(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            db = Path(tmp) / "joselyn.db"
            hr = Principal(id="HR-1", role="HR Manager")
            with PeopleStore(db, principal=hr) as store:
                store.import_batch(
                    IntakeBatch(
                        source="people.csv",
                        source_format="csv",
                        records=[self._record()],
                    )
                )

            auditor = Principal(id="AUD-1", role="Auditor")
            with PeopleStore(db, principal=auditor) as store:
                self.assertEqual(store.history("mara@example.com"), [])
                self.assertEqual(len(store.history("EMP-9")), 1)


if __name__ == "__main__":
    unittest.main()
