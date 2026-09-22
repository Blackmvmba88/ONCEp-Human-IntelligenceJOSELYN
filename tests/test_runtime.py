import unittest

from joselyn.event_bus import InMemoryEventBus
from joselyn.models import Actor, DomainEvent
from joselyn.runtime import HumanIntelligenceRuntime


class RuntimeTests(unittest.TestCase):
    def test_event_envelope_and_audit_share_correlation_id(self) -> None:
        runtime = HumanIntelligenceRuntime()
        event, report = runtime.emit(
            "employee.created",
            actor=Actor(type="user", id="USER-1"),
            tenant_id="TENANT-1",
            payload={"employee_id": "EMP-204"},
        )

        self.assertTrue(report.ok)
        self.assertEqual(event.event_version, 1)
        self.assertEqual(event.correlation_id, runtime.audit_log[0].correlation_id)
        self.assertEqual(runtime.audit_log[0].resource_id, event.event_id)

    def test_bus_is_idempotent_per_event_and_handler(self) -> None:
        bus = InMemoryEventBus()
        calls: list[str] = []

        def project_employee(event: DomainEvent) -> None:
            calls.append(event.event_id)

        bus.subscribe("employee.created", project_employee)
        event = DomainEvent.create(
            "employee.created",
            actor=Actor(type="system", id="test"),
            tenant_id="TENANT-1",
        )

        first = bus.publish(event)
        second = bus.publish(event)

        self.assertEqual(len(calls), 1)
        self.assertEqual(len(first.delivered), 1)
        self.assertEqual(len(second.skipped), 1)

    def test_handler_failure_is_visible_and_retryable(self) -> None:
        bus = InMemoryEventBus()
        attempts = 0

        def unstable(_: DomainEvent) -> None:
            nonlocal attempts
            attempts += 1
            if attempts == 1:
                raise RuntimeError("temporary")

        bus.subscribe("contract.expiring", unstable)
        event = DomainEvent.create(
            "contract.expiring",
            actor=Actor(type="system", id="scheduler"),
            tenant_id="TENANT-1",
        )

        first = bus.publish(event)
        second = bus.publish(event)

        self.assertFalse(first.ok)
        self.assertTrue(second.ok)
        self.assertEqual(attempts, 2)
        self.assertEqual(len(second.delivered), 1)


if __name__ == "__main__":
    unittest.main()
