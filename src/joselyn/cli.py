from __future__ import annotations

import argparse
import json
from typing import Sequence

from . import __version__
from .intake import capabilities, load_path
from .models import Actor
from .runtime import HumanIntelligenceRuntime
from .work import WorkRequest, assess_automation


def _add_format_option(parser: argparse.ArgumentParser) -> None:
    parser.add_argument("--format", choices=("table", "json"), default="table")


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        prog="joselyn",
        description="JOSELYN CLI — technical cockpit for PONCE",
    )

    sub = parser.add_subparsers(dest="command", required=True)

    status = sub.add_parser("status", help="show runtime status")
    _add_format_option(status)

    version = sub.add_parser("version", help="show CLI version")
    _add_format_option(version)

    formats = sub.add_parser("formats", help="show HR intake format capabilities")
    _add_format_option(formats)

    intake = sub.add_parser("intake", help="inspect and normalize HR source data")
    intake_sub = intake.add_subparsers(dest="intake_command", required=True)
    inspect = intake_sub.add_parser("inspect", help="inspect CSV/TSV/JSON without persisting it")
    inspect.add_argument("path")
    _add_format_option(inspect)

    work = sub.add_parser("work", help="measure work value and automation opportunity")
    work_sub = work.add_subparsers(dest="work_command", required=True)
    assess = work_sub.add_parser("assess", help="score an HR work request for automation")
    assess.add_argument("--title", required=True)
    assess.add_argument("--purpose", required=True)
    assess.add_argument("--requester", required=True)
    assess.add_argument("--priority", type=int, default=3)
    assess.add_argument("--frequency", type=float, default=1.0, dest="frequency_per_month")
    assess.add_argument("--minutes", type=float, default=10.0, dest="minutes_per_run")
    assess.add_argument("--impact", type=int, default=3, dest="business_impact")
    assess.add_argument("--compliance-impact", type=int, default=0)
    assess.add_argument("--human-judgment", action="store_true")
    assess.add_argument("--structured-inputs", action="store_true")
    assess.add_argument("--repeated-steps", action="store_true")
    _add_format_option(assess)

    event = sub.add_parser("event", help="domain event tools")
    event_sub = event.add_subparsers(dest="event_command", required=True)
    demo = event_sub.add_parser("demo", help="emit a local bootstrap event")
    demo.add_argument("--type", default="employee.created", dest="event_type")
    demo.add_argument("--tenant", default="local")
    demo.add_argument("--actor", default="joselyn-cli")
    _add_format_option(demo)

    return parser


def _print_mapping(data: dict[str, object], output_format: str) -> None:
    if output_format == "json":
        print(json.dumps(data, indent=2, default=str, ensure_ascii=False))
        return

    if not data:
        return
    width = max(len(str(key)) for key in data)
    for key, value in data.items():
        print(f"{key:<{width}}  {value}")


def _print_formats(output_format: str) -> None:
    items = capabilities()
    if output_format == "json":
        print(json.dumps(items, indent=2, ensure_ascii=False))
        return
    for item in items:
        extensions = ", ".join(item["extensions"])
        print(f"{item['name']:<8} {item['status']:<16} {extensions:<24} {item['notes']}")


def _intake_summary(path: str) -> dict[str, object]:
    batch = load_path(path)
    warning_count = sum(len(record.warnings) for record in batch.records)
    mapped_fields = sorted({field for record in batch.records for field in record.data})
    extra_fields = sorted({field for record in batch.records for field in record.extra_fields})
    return {
        "source": batch.source,
        "source_format": batch.source_format,
        "record_count": len(batch.records),
        "duplicate_count": len(batch.duplicate_keys),
        "duplicate_keys": batch.duplicate_keys,
        "warning_count": warning_count,
        "mapped_fields": mapped_fields,
        "unmapped_fields": extra_fields,
    }


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

    if args.command == "formats":
        _print_formats(args.format)
        return 0

    if args.command == "intake" and args.intake_command == "inspect":
        try:
            result = _intake_summary(args.path)
        except (OSError, ValueError, json.JSONDecodeError) as exc:
            _print_mapping({"error": f"{type(exc).__name__}: {exc}"}, args.format)
            return 1
        _print_mapping(result, args.format)
        return 0

    if args.command == "work" and args.work_command == "assess":
        try:
            request = WorkRequest(
                title=args.title,
                purpose=args.purpose,
                requester=args.requester,
                priority=args.priority,
                frequency_per_month=args.frequency_per_month,
                minutes_per_run=args.minutes_per_run,
                business_impact=args.business_impact,
                compliance_impact=args.compliance_impact,
                requires_human_judgment=args.human_judgment,
                structured_inputs=args.structured_inputs,
                repeated_steps=args.repeated_steps,
            )
            assessment = assess_automation(request)
        except ValueError as exc:
            _print_mapping({"error": str(exc)}, args.format)
            return 1
        result = {"request": request.to_dict(), "assessment": assessment.to_dict()}
        _print_mapping(result, args.format)
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
