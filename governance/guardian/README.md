# Guardian

Repository health monitoring system for the Infinity Template Library.

## Overview

Guardian continuously monitors CI/CD pipeline health, test coverage, pull request activity, and dependency freshness. It raises typed `HealthAlert` objects and can suggest automated fixes for each alert kind.

## Components

| Module | Purpose |
|--------|---------|
| `GuardianSystem` | Core check engine |
| `HealthAlert` | Typed alert model (Pydantic) |
| `AutoFixSuggestion` | Actionable remediation suggestion |
| `GuardianReport` | Aggregated health snapshot |

## Alert Types

| Type | Severity | Trigger |
|------|----------|---------|
| `failed_workflow` | critical | Any workflow run with `conclusion=failure` |
| `stale_workflow` | warning | In-progress run older than 2 hours |
| `repeated_failures` | critical | Same workflow failing more than 3 times |
| `coverage_drop` | warning | Coverage below configurable threshold (default 80 %) |
| `stale_pr` | warning | Non-draft PR without update for more than 7 days |
| `stale_dependency` | warning | Dependency entry older than 90 days |

## Quick Start

```bash
pip install -r requirements.txt
python src/guardian.py
```

## Running Tests

```bash
pip install -r requirements-dev.txt
pytest
```

## Docker

```bash
docker build -t guardian .
docker run --rm guardian
```

## Usage Example

```python
from guardian import GuardianSystem

guardian = GuardianSystem()

alerts = guardian.check_workflow_health(workflow_runs)
alerts += guardian.check_stale_prs(open_prs)

cov_alert = guardian.check_test_coverage(coverage_pct=72.5)
if cov_alert:
    alerts.append(cov_alert)

for alert in alerts:
    fix = guardian.suggest_autofix(alert)
    if fix:
        print(f"Suggested fix: {fix.command}")

report = guardian.generate_report(alerts)
print(f"Overall health: {report.overall_health}")
```
