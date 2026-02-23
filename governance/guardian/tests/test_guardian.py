from datetime import datetime, timezone, timedelta

import pytest

from guardian import GuardianSystem, HealthAlert


def make_run(
    run_id: int,
    name: str,
    status: str = "completed",
    conclusion: str | None = None,
    hours_ago: float = 1,
) -> dict:
    now = datetime.now(timezone.utc)
    created = (now - timedelta(hours=hours_ago)).isoformat()
    return {
        "id": run_id,
        "name": name,
        "status": status,
        "conclusion": conclusion,
        "created_at": created,
        "updated_at": created,
    }


def make_pr(
    pr_id: int,
    title: str,
    days_ago: int = 10,
    draft: bool = False,
) -> dict:
    now = datetime.now(timezone.utc)
    updated = (now - timedelta(days=days_ago)).isoformat()
    return {
        "id": pr_id,
        "title": title,
        "created_at": updated,
        "updated_at": updated,
        "draft": draft,
    }


guardian = GuardianSystem()


def test_failed_workflow_alert() -> None:
    runs = [make_run(1, "CI", conclusion="failure")]
    alerts = guardian.check_workflow_health(runs)
    assert any(a.type == "failed_workflow" for a in alerts)
    assert any(a.severity == "critical" for a in alerts)


def test_stale_pr_alert() -> None:
    prs = [make_pr(42, "Feature branch", days_ago=10)]
    alerts = guardian.check_stale_prs(prs)
    assert len(alerts) == 1
    assert alerts[0].type == "stale_pr"
    assert alerts[0].severity == "warning"
    # Draft PRs must not be flagged
    draft_prs = [make_pr(43, "WIP feature", days_ago=20, draft=True)]
    assert guardian.check_stale_prs(draft_prs) == []


def test_coverage_drop_alert() -> None:
    alert = guardian.check_test_coverage(70.0, threshold=80.0)
    assert alert is not None
    assert alert.type == "coverage_drop"
    assert alert.severity == "warning"
    # Coverage at threshold must not trigger
    assert guardian.check_test_coverage(80.0, threshold=80.0) is None
    # Coverage above threshold must not trigger
    assert guardian.check_test_coverage(95.0, threshold=80.0) is None


def test_autofix_suggestion() -> None:
    alert = HealthAlert(
        type="failed_workflow",
        severity="critical",
        title="Workflow failed: CI",
        description="Workflow run 1 for 'CI' has failed.",
        component="CI",
        action_required=True,
        metadata={"name": "CI"},
    )
    suggestion = guardian.suggest_autofix(alert)
    assert suggestion is not None
    assert "CI" in suggestion.action
    assert "gh workflow run" in suggestion.command

    # Coverage drop autofix
    cov_alert = HealthAlert(
        type="coverage_drop",
        severity="warning",
        title="Test coverage below threshold",
        description="Coverage is 70.0%, below the 80.0% threshold.",
        component="test-coverage",
        action_required=True,
    )
    cov_fix = guardian.suggest_autofix(cov_alert)
    assert cov_fix is not None
    assert "tests" in cov_fix.action.lower()

    # Stale dependency autofix
    dep_alert = HealthAlert(
        type="stale_dependency",
        severity="warning",
        title="Stale dependency: requests",
        description="requests is 120 days old (current: 2.28.0, latest: 2.31.0).",
        component="requests",
        action_required=True,
        metadata={"latest_version": "2.31.0"},
    )
    dep_fix = guardian.suggest_autofix(dep_alert)
    assert dep_fix is not None
    assert "2.31.0" in dep_fix.action

    # Unknown type returns None
    unknown = HealthAlert(
        type="unknown_type",
        severity="warning",
        title="Unknown",
        description="Unknown",
        component="unknown",
        action_required=False,
    )
    assert guardian.suggest_autofix(unknown) is None


def test_guardian_report_health_status() -> None:
    critical_alert = HealthAlert(
        type="failed_workflow",
        severity="critical",
        title="Workflow failed: CI",
        description="Test",
        component="CI",
        action_required=True,
    )
    report = guardian.generate_report([critical_alert])
    assert report.overall_health == "critical"
    assert report.critical_count == 1
    assert report.warning_count == 0
    assert report.total_alerts == 1

    warning_alert = HealthAlert(
        type="stale_pr",
        severity="warning",
        title="Stale PR",
        description="Test",
        component="pr-1",
        action_required=True,
    )
    degraded_report = guardian.generate_report([warning_alert])
    assert degraded_report.overall_health == "degraded"
    assert degraded_report.warning_count == 1


def test_no_alerts_returns_ok() -> None:
    report = guardian.generate_report([])
    assert report.overall_health == "ok"
    assert report.total_alerts == 0
    assert report.critical_count == 0
    assert report.warning_count == 0
