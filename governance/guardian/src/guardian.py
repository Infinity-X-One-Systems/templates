from __future__ import annotations

from datetime import datetime, timezone
from typing import Optional

from pydantic import BaseModel, Field


class HealthAlert(BaseModel):
    type: str
    severity: str  # "critical" | "warning"
    title: str
    description: str
    component: str
    action_required: bool
    metadata: dict = Field(default_factory=dict)


class AutoFixSuggestion(BaseModel):
    action: str
    command: str
    rationale: str


class GuardianReport(BaseModel):
    total_alerts: int
    critical_count: int
    warning_count: int
    alerts: list[HealthAlert]
    timestamp: datetime
    overall_health: str  # "ok" | "degraded" | "critical"


class GuardianSystem:
    def check_workflow_health(self, runs: list[dict]) -> list[HealthAlert]:
        alerts: list[HealthAlert] = []
        now = datetime.now(timezone.utc)
        failure_counts: dict[str, int] = {}

        for run in runs:
            name = run.get("name", "unknown")
            run_id = run.get("id", "unknown")

            if run.get("conclusion") == "failure":
                failure_counts[name] = failure_counts.get(name, 0) + 1
                alerts.append(
                    HealthAlert(
                        type="failed_workflow",
                        severity="critical",
                        title=f"Workflow failed: {name}",
                        description=f"Workflow run {run_id} for '{name}' has failed.",
                        component=name,
                        action_required=True,
                        metadata={"run_id": run_id, "name": name},
                    )
                )

            if run.get("status") == "in_progress":
                created_at_str = run.get("created_at", "")
                try:
                    created_at = datetime.fromisoformat(
                        created_at_str.replace("Z", "+00:00")
                    )
                    elapsed_hours = (now - created_at).total_seconds() / 3600
                    if elapsed_hours > 2:
                        alerts.append(
                            HealthAlert(
                                type="stale_workflow",
                                severity="warning",
                                title=f"Stale in-progress workflow: {name}",
                                description=(
                                    f"Workflow run {run_id} for '{name}' has been "
                                    f"in progress for {elapsed_hours:.1f} hours."
                                ),
                                component=name,
                                action_required=True,
                                metadata={"run_id": run_id, "elapsed_hours": elapsed_hours},
                            )
                        )
                except (ValueError, AttributeError):
                    pass

        for name, count in failure_counts.items():
            if count > 3:
                alerts.append(
                    HealthAlert(
                        type="repeated_failures",
                        severity="critical",
                        title=f"Repeated failures detected: {name}",
                        description=f"Workflow '{name}' has failed {count} times.",
                        component=name,
                        action_required=True,
                        metadata={"failure_count": count},
                    )
                )

        return alerts

    def check_test_coverage(
        self, coverage_pct: float, threshold: float = 80.0
    ) -> Optional[HealthAlert]:
        if coverage_pct < threshold:
            return HealthAlert(
                type="coverage_drop",
                severity="warning",
                title="Test coverage below threshold",
                description=(
                    f"Coverage is {coverage_pct:.1f}%, below the "
                    f"{threshold:.1f}% threshold."
                ),
                component="test-coverage",
                action_required=True,
                metadata={"coverage_pct": coverage_pct, "threshold": threshold},
            )
        return None

    def check_stale_prs(self, prs: list[dict]) -> list[HealthAlert]:
        alerts: list[HealthAlert] = []
        now = datetime.now(timezone.utc)

        for pr in prs:
            if pr.get("draft"):
                continue

            updated_at_str = pr.get("updated_at", "")
            try:
                updated_at = datetime.fromisoformat(
                    updated_at_str.replace("Z", "+00:00")
                )
                age_days = (now - updated_at).days
                if age_days > 7:
                    pr_id = pr.get("id", "unknown")
                    title = pr.get("title", "Untitled PR")
                    alerts.append(
                        HealthAlert(
                            type="stale_pr",
                            severity="warning",
                            title=f"Stale PR: {title}",
                            description=(
                                f"PR #{pr_id} has not been updated in {age_days} days."
                            ),
                            component=f"pr-{pr_id}",
                            action_required=True,
                            metadata={"pr_id": pr_id, "age_days": age_days},
                        )
                    )
            except (ValueError, AttributeError):
                pass

        return alerts

    def check_dependency_age(self, deps: list[dict]) -> list[HealthAlert]:
        alerts: list[HealthAlert] = []

        for dep in deps:
            age_days = dep.get("age_days", 0)
            if age_days > 90:
                name = dep.get("name", "unknown")
                current_version = dep.get("current_version", "unknown")
                latest_version = dep.get("latest_version", "unknown")
                alerts.append(
                    HealthAlert(
                        type="stale_dependency",
                        severity="warning",
                        title=f"Stale dependency: {name}",
                        description=(
                            f"{name} is {age_days} days old "
                            f"(current: {current_version}, latest: {latest_version})."
                        ),
                        component=name,
                        action_required=True,
                        metadata={
                            "current_version": current_version,
                            "latest_version": latest_version,
                            "age_days": age_days,
                        },
                    )
                )

        return alerts

    def suggest_autofix(self, alert: HealthAlert) -> Optional[AutoFixSuggestion]:
        if alert.type == "failed_workflow":
            name = alert.component
            return AutoFixSuggestion(
                action=f"Re-run workflow {name}",
                command=f"gh workflow run '{name}'",
                rationale="Re-running the workflow may resolve transient failures.",
            )

        if alert.type == "coverage_drop":
            return AutoFixSuggestion(
                action="Add tests for uncovered paths",
                command="pytest --cov=src --cov-report=html",
                rationale="Improving test coverage ensures code reliability.",
            )

        if alert.type == "stale_pr":
            pr_id = alert.metadata.get("pr_id") or alert.component.replace("pr-", "")
            return AutoFixSuggestion(
                action=f"Request review or close PR #{pr_id}",
                command=f"gh pr review {pr_id} --request-changes",
                rationale=(
                    "Stale PRs block development momentum "
                    "and should be reviewed or closed."
                ),
            )

        if alert.type == "stale_dependency":
            name = alert.component
            latest_version = alert.metadata.get("latest_version", "latest")
            return AutoFixSuggestion(
                action=f"Update {name} to {latest_version}",
                command=f"pip install --upgrade {name}",
                rationale=(
                    f"Keeping {name} up-to-date prevents security vulnerabilities "
                    "and compatibility issues."
                ),
            )

        return None

    def generate_report(self, alerts: list[HealthAlert]) -> GuardianReport:
        critical_count = sum(1 for a in alerts if a.severity == "critical")
        warning_count = sum(1 for a in alerts if a.severity == "warning")

        if critical_count > 0:
            overall_health = "critical"
        elif warning_count > 0:
            overall_health = "degraded"
        else:
            overall_health = "ok"

        return GuardianReport(
            total_alerts=len(alerts),
            critical_count=critical_count,
            warning_count=warning_count,
            alerts=alerts,
            timestamp=datetime.now(timezone.utc),
            overall_health=overall_health,
        )


if __name__ == "__main__":
    guardian = GuardianSystem()
    report = guardian.generate_report([])
    print(f"Guardian system initialized. Overall health: {report.overall_health}")
