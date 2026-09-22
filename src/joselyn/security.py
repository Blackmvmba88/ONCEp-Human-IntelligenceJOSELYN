from __future__ import annotations

from dataclasses import dataclass


class AccessDenied(PermissionError):
    """Raised when a principal lacks an explicit JOSELYN permission."""


ROLE_PERMISSIONS: dict[str, frozenset[str]] = {
    "Super Admin": frozenset({"*"}),
    "HR Director": frozenset({
        "employee.read.basic",
        "employee.read.contact",
        "employee.read.extra",
        "employee.read.provenance",
        "employee.import",
        "employee.update.profile",
        "employee.history.read",
    }),
    "HR Manager": frozenset({
        "employee.read.basic",
        "employee.read.contact",
        "employee.read.extra",
        "employee.read.provenance",
        "employee.import",
        "employee.update.profile",
        "employee.history.read",
    }),
    "Recruiter": frozenset({
        "employee.read.basic",
        "employee.read.contact",
    }),
    "Payroll Operator": frozenset({
        "employee.read.basic",
        "employee.read.contact",
    }),
    "Manager": frozenset({
        "employee.read.basic",
    }),
    # Employee self-service needs subject-aware authorization before it is safe.
    "Employee": frozenset(),
    "Auditor": frozenset({
        "employee.read.basic",
        "employee.read.provenance",
        "employee.history.read",
    }),
    "Integration Service": frozenset({
        "employee.read.basic",
        "employee.read.contact",
        "employee.read.provenance",
        "employee.import",
        "employee.update.profile",
        "employee.history.read",
    }),
}


@dataclass(frozen=True, slots=True)
class Principal:
    id: str
    role: str

    def __post_init__(self) -> None:
        if not self.id.strip():
            raise ValueError("principal.id is required")
        if self.role not in ROLE_PERMISSIONS:
            known = ", ".join(sorted(ROLE_PERMISSIONS))
            raise ValueError(f"unknown role {self.role!r}; known roles: {known}")

    def can(self, permission: str) -> bool:
        granted = ROLE_PERMISSIONS[self.role]
        return "*" in granted or permission in granted

    def require(self, permission: str) -> None:
        if not self.can(permission):
            raise AccessDenied(
                f"principal {self.id!r} with role {self.role!r} lacks {permission}"
            )
