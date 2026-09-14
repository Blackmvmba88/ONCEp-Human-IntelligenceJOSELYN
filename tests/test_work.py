import unittest

from joselyn.work import WorkRequest, assess_automation


class WorkAssessmentTests(unittest.TestCase):
    def test_repetitive_structured_work_is_high_automation_candidate(self) -> None:
        request = WorkRequest(
            title="Consolidar incidencias",
            purpose="Preparar pre-nomina",
            requester="HR Manager",
            frequency_per_month=8,
            minutes_per_run=45,
            business_impact=4,
            structured_inputs=True,
            repeated_steps=True,
        )

        result = assess_automation(request)
        self.assertEqual(result.recommendation, "automate-now")
        self.assertGreaterEqual(result.automation_score, 6)
        self.assertEqual(result.monthly_minutes_exposed, 360.0)

    def test_human_judgment_reduces_full_automation_score(self) -> None:
        request = WorkRequest(
            title="Decidir promocion",
            purpose="Evaluar promocion interna",
            requester="Director",
            frequency_per_month=2,
            minutes_per_run=60,
            business_impact=5,
            requires_human_judgment=True,
            repeated_steps=True,
        )

        result = assess_automation(request)
        self.assertNotEqual(result.recommendation, "automate-now")
        self.assertTrue(any("human judgment" in reason for reason in result.reasons))

    def test_invalid_scale_is_rejected(self) -> None:
        with self.assertRaises(ValueError):
            WorkRequest(
                title="x",
                purpose="y",
                requester="z",
                priority=9,
            )


if __name__ == "__main__":
    unittest.main()
