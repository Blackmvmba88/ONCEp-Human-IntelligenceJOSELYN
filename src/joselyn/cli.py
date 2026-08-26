from __future__ import annotations

import argparse
import json
from typing import Sequence

from . import __version__
from .models import Actor
from .runtime import HumanIntelligenceRuntime


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        prog="joselyn",
        description="JOSELYN CLI — technical cockpit for PONCE",
    )
    parser.add_argument("--format", choices=("table", "json"), default="table")

    sub = parser.add_subparsers(dest="command", required=True)
    sub.add_parser("status", help="show runtime status")
    sub.add_parser("version", help="show CLI version")

    event = sub.add_parser("event", help="domain event tools")
    event_sub = event.add_subparsers(dest="event_command", required=True)
    demo = event_sub.add_parser("demo", help="emit a local bootstrap event")
    demo.add_argument("--type", default="employee.created", dest="event_type")
    demo.add_argument("--tenant", default="local")
    demo.add_argument("--actor", default="joselyn-cli")

    return parser


def _print_mapping(data: dict[str, object], output_format: str) -> None:
    if output_format == "json":
        print(json.dumps(data, indent=2, default=str))
        return

    width = max(len(str(key)) for key in data)
    for key, value in data.items():
        print(f"{key:<{width}}  {value}")


def main(argv: Sequence[str] | None = None) -> int:
    parser = build_parser()
    args = parser.parse_args(argv)
    runtime = HumanIntelligenceRuntime()

    if args.command == "version":
        _print_mapping({"joselyn": __version__}, args.format)
        return 0

    if args.command == "status":
        _print_mapping(runtime.status(), args.format)
        return 0

    if args.command == "event" and args.event_command == "demo":
        event, report = runtime.emit(
            args.event_type,
            actor=Actor(type="user", id=args.actor),
            tenant_id=args.tenant,
            payload={"mode": "bootstrap-demo"},
        )
        result = {
            "event_id": event.event_id,
            "event_type": event.event_type,
            "correlation_id": event.correlation_id,
            "delivered": report.delivered,
            "skipped": report.skipped,
            "failed": [failure.error for failure in report.failed],
            "audit_records": len(runtime.audit_log),
        }
        _print_mapping(result, args.format)
        return 0 if report.ok else 1

    parser.error("unsupported command")
    return 2


if __name__ == "__main__":
    raise SystemExit(main())
