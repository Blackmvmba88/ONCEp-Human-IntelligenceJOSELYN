from pathlib import Path
from tempfile import TemporaryDirectory
import unittest

from joselyn.app import HR_ACTIONS, build_dashboard
from joselyn.intake import normalize_row
from joselyn.people import PeopleStore


class AppTests(unittest.TestCase):
    def test_hr_action_catalog_exposes_daily_work(self) -> None:
        titles = {item["title"] for item in HR_ACTIONS}
        self.assertIn("Nuevo ingreso", titles)
        self.assertIn("Buscar persona", titles)
        self.assertIn("Vacaciones y permisos", titles)
        self.assertIn("Documentos", titles)
        self.assertIn("Reclutamiento", titles)
        self.assertIn("Incidencias", titles)
        self.assertIn("Aprobaciones", titles)
        self.assertIn("Reportes", titles)

    def test_dashboard_uses_people_core(self) -> None:
        with TemporaryDirectory() as directory:
            db = Path(directory) / "joselyn.db"
            with PeopleStore(db) as store:
                complete = normalize_row(
                    {
                        "employee_id": "EMP-1",
                        "full_name": "Ana Pérez",
                        "email": "ana@example.com",
                        "department": "RH",
                        "position": "Jefa",
                        "start_date": "2026-10-01",
                        "status": "activo",
                    },
                    source="test",
                    row_number=1,
                )
                incomplete = normalize_row(
                    {"employee_id": "EMP-2", "full_name": "Luis", "status": "activo"},
                    source="test",
                    row_number=2,
                )
                store.upsert(complete, source="test")
                store.upsert(incomplete, source="test")
                dashboard = build_dashboard(store)

            self.assertEqual(dashboard["summary"]["people"], 2)
            self.assertEqual(dashboard["summary"]["active"], 2)
            self.assertEqual(dashboard["summary"]["incomplete_records"], 1)


if __name__ == "__main__":
    unittest.main()
