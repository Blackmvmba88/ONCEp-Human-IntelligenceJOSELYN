from __future__ import annotations

from dataclasses import asdict, dataclass
from typing import Any


@dataclass(frozen=True, slots=True)
class WorkRequest:
    title: str
    purpose: str
    requester: str
    priority: int = 3
    frequency_per_month: float = 1.0
    minutes_per_run: float = 10.0
    business_impact: int = 3
    compliance_impact: int = 0
    requires_human_judgment: bool = False
    structured_inputs: bool = False
    repeated_steps: bool = False

    def __post_init__(self) -> None:
        if not self.title.strip():
            raise ValueError("title is required")
        if not self.purpose.strip():
            raise ValueError("purpose is required")
        if not self.requester.strip():
            raise ValueError("requester is required")
        if not 1 <= self.priority <= 5:
            raise ValueError("priority must be between 1 and 5")
        if not 0 <= self.business_impact <= 5:
            raise ValueError("business_impact must be between 0 and 5")
        if not 0 <= self.compliance_impact <= 5:
            raise ValueError("compliance_impact must be between 0 and 5")
        if self.frequency_per_month < 0 or self.minutes_per_run < 0:
            raise ValueError("frequency and time must be non-negative")

    @property
    def monthly_minutes(self) -> float:
        return self.frequency_per_month * self.minutes_per_run

    def to_dict(self) -> dict[str, Any]:
        payload = asdict(self)
        payload["monthly_minutes"] = round(self.monthly_minutes, 2)
        return payload


@dataclass(frozen=True, slots=True)
class AutomationAssessment:
    automation_score: int
    recommendation: str
    reasons: tuple[str, ...]
    monthly_minutes_exposed: float

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)


def assess_automation(request: WorkRequest) -> AutomationAssessment:
    score = 0
    reasons: list[str] = []

    if request.frequency_per_month >= 4:
        score += 2
        reasons.append("repeats frequently")
    elif request.frequency_per_month >= 2:
        score += 1
        reasons.append("repeats more than once per month")

    if request.minutes_per_run >= 30:
        score += 2
        reasons.append("consumes meaningful time per execution")
    elif request.minutes_per_run >= 10:
        score += 1
        reasons.append("has measurable execution cost")

    if request.structured_inputs:
        score += 2
        reasons.append("uses structured or mappable inputs")

    if request.repeated_steps:
        score += 2
        reasons.append("contains repeated deterministic steps")

    if request.requires_human_judgment:
        score -= 2
        reasons.append("requires human judgment; automate preparation, not the decision")

    if request.compliance_impact >= 4:
        score -= 1
        reasons.append("high compliance impact requires stronger human approval gates")

    score = max(0, min(8, score))
    if score >= 6:
        recommendation = "automate-now"
    elif score >= 3:
        recommendation = "assist-and-measure"
    else:
        recommendation = "keep-human-led"

    return AutomationAssessment(
        automation_score=score,
        recommendation=recommendation,
        reasons=tuple(reasons),
        monthly_minutes_exposed=round(request.monthly_minutes, 2),
    )
