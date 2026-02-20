"""Tests for the Memory & Rehydration system scripts."""

from __future__ import annotations

import json
import subprocess
import sys
from pathlib import Path

import pytest

# Resolve script paths relative to this file.
_SCRIPTS_DIR = Path(__file__).resolve().parent.parent / "scripts"
_REHYDRATE = str(_SCRIPTS_DIR / "rehydrate.py")
_WRITE_STATE = str(_SCRIPTS_DIR / "write_state.py")
_LOG_DECISION = str(_SCRIPTS_DIR / "log_decision.py")
_LOG_TELEMETRY = str(_SCRIPTS_DIR / "log_telemetry.py")


# ---------------------------------------------------------------------------
# rehydrate.py
# ---------------------------------------------------------------------------


def test_rehydrate_empty_dir(tmp_path: Path) -> None:
    """Running rehydrate.py on an empty directory exits with code 0."""
    result = subprocess.run(
        [sys.executable, _REHYDRATE, "--state-dir", str(tmp_path)],
        capture_output=True,
        text=True,
    )
    assert result.returncode == 0, result.stderr
    context = json.loads(result.stdout)
    assert "warnings" in context
    # All four keys should be present but None (files missing).
    for key in ("system_state", "decision_log", "architecture_map", "telemetry"):
        assert key in context
        assert context[key] is None


def test_rehydrate_with_state_file(tmp_path: Path) -> None:
    """rehydrate.py validates a valid system_state.json without warnings."""
    state = {
        "manifest_version": "1.0.0",
        "system_name": "test-system",
        "org": "test-org",
        "phase": "building",
        "components_status": {},
        "last_action": "test",
        "last_action_at": "2024-01-01T00:00:00+00:00",
        "health_score": 90,
        "errors": [],
        "warnings": [],
    }
    (tmp_path / "system_state.json").write_text(json.dumps(state))

    result = subprocess.run(
        [sys.executable, _REHYDRATE, "--state-dir", str(tmp_path)],
        capture_output=True,
        text=True,
    )
    assert result.returncode == 0, result.stderr
    context = json.loads(result.stdout)
    assert context["system_state"]["system_name"] == "test-system"


def test_rehydrate_output_file(tmp_path: Path) -> None:
    """rehydrate.py writes context JSON to --output path."""
    out_file = tmp_path / "ctx" / "context.json"
    result = subprocess.run(
        [
            sys.executable,
            _REHYDRATE,
            "--state-dir",
            str(tmp_path),
            "--output",
            str(out_file),
        ],
        capture_output=True,
        text=True,
    )
    assert result.returncode == 0, result.stderr
    assert out_file.exists()
    context = json.loads(out_file.read_text())
    assert "warnings" in context


# ---------------------------------------------------------------------------
# write_state.py
# ---------------------------------------------------------------------------


def test_write_state_creates_file(tmp_path: Path) -> None:
    """write_state.py creates system_state.json when it does not exist."""
    result = subprocess.run(
        [
            sys.executable,
            _WRITE_STATE,
            "--state-dir",
            str(tmp_path),
            "--action",
            "initialise",
        ],
        capture_output=True,
        text=True,
    )
    assert result.returncode == 0, result.stderr
    state_file = tmp_path / "system_state.json"
    assert state_file.exists()
    state = json.loads(state_file.read_text())
    assert state["last_action"] == "initialise"


def test_write_state_updates_phase(tmp_path: Path) -> None:
    """write_state.py updates the phase field correctly."""
    # First call creates the file.
    subprocess.run(
        [sys.executable, _WRITE_STATE, "--state-dir", str(tmp_path), "--phase", "planning"],
        check=True,
    )
    # Second call updates the phase.
    subprocess.run(
        [sys.executable, _WRITE_STATE, "--state-dir", str(tmp_path), "--phase", "building"],
        check=True,
    )
    state = json.loads((tmp_path / "system_state.json").read_text())
    assert state["phase"] == "building"


def test_write_state_updates_component_status(tmp_path: Path) -> None:
    """write_state.py stores component status correctly."""
    subprocess.run(
        [
            sys.executable,
            _WRITE_STATE,
            "--state-dir",
            str(tmp_path),
            "--component",
            "api",
            "--status",
            "healthy",
        ],
        check=True,
    )
    state = json.loads((tmp_path / "system_state.json").read_text())
    assert state["components_status"]["api"] == "healthy"


def test_write_state_updates_health_score(tmp_path: Path) -> None:
    """write_state.py sets health_score correctly."""
    subprocess.run(
        [
            sys.executable,
            _WRITE_STATE,
            "--state-dir",
            str(tmp_path),
            "--health-score",
            "72",
        ],
        check=True,
    )
    state = json.loads((tmp_path / "system_state.json").read_text())
    assert state["health_score"] == 72


def test_write_state_invalid_health_score(tmp_path: Path) -> None:
    """write_state.py exits non-zero for out-of-range health score."""
    result = subprocess.run(
        [
            sys.executable,
            _WRITE_STATE,
            "--state-dir",
            str(tmp_path),
            "--health-score",
            "150",
        ],
        capture_output=True,
        text=True,
    )
    assert result.returncode != 0


# ---------------------------------------------------------------------------
# log_decision.py
# ---------------------------------------------------------------------------


def test_log_decision_creates_file(tmp_path: Path) -> None:
    """log_decision.py creates decision_log.json when it does not exist."""
    result = subprocess.run(
        [
            sys.executable,
            _LOG_DECISION,
            "--state-dir",
            str(tmp_path),
            "--type",
            "architecture",
            "--description",
            "Use PostgreSQL",
            "--rationale",
            "ACID compliance",
            "--made-by",
            "human",
        ],
        capture_output=True,
        text=True,
    )
    assert result.returncode == 0, result.stderr
    log_file = tmp_path / "decision_log.json"
    assert log_file.exists()
    log = json.loads(log_file.read_text())
    assert isinstance(log, list)
    assert len(log) == 1
    assert log[0]["decision_type"] == "architecture"


def test_log_decision_appends(tmp_path: Path) -> None:
    """log_decision.py appends entries to an existing decision_log.json."""
    for i in range(3):
        subprocess.run(
            [
                sys.executable,
                _LOG_DECISION,
                "--state-dir",
                str(tmp_path),
                "--type",
                "tooling",
                "--description",
                f"Decision {i}",
                "--rationale",
                "reason",
                "--made-by",
                "agent",
            ],
            check=True,
        )
    log = json.loads((tmp_path / "decision_log.json").read_text())
    assert len(log) == 3


def test_log_decision_with_components(tmp_path: Path) -> None:
    """log_decision.py records related_components correctly."""
    subprocess.run(
        [
            sys.executable,
            _LOG_DECISION,
            "--state-dir",
            str(tmp_path),
            "--type",
            "process",
            "--description",
            "Enable CI",
            "--rationale",
            "quality gates",
            "--made-by",
            "human",
            "--component",
            "backend",
            "--component",
            "frontend",
        ],
        check=True,
    )
    log = json.loads((tmp_path / "decision_log.json").read_text())
    assert set(log[0]["related_components"]) == {"backend", "frontend"}


# ---------------------------------------------------------------------------
# log_telemetry.py
# ---------------------------------------------------------------------------


def test_log_telemetry_creates_file(tmp_path: Path) -> None:
    """log_telemetry.py creates telemetry.json when it does not exist."""
    result = subprocess.run(
        [
            sys.executable,
            _LOG_TELEMETRY,
            "--state-dir",
            str(tmp_path),
            "--event-type",
            "health_check",
            "--component",
            "api",
        ],
        capture_output=True,
        text=True,
    )
    assert result.returncode == 0, result.stderr
    assert (tmp_path / "telemetry.json").exists()


def test_log_telemetry_appends(tmp_path: Path) -> None:
    """log_telemetry.py appends multiple events to telemetry.json."""
    for event_type in ("test_pass", "test_fail", "deploy"):
        subprocess.run(
            [
                sys.executable,
                _LOG_TELEMETRY,
                "--state-dir",
                str(tmp_path),
                "--event-type",
                event_type,
                "--component",
                "backend",
                "--value",
                "42",
                "--unit",
                "ms",
            ],
            check=True,
        )
    events = json.loads((tmp_path / "telemetry.json").read_text())
    assert len(events) == 3
    assert events[0]["event_type"] == "test_pass"
    assert events[1]["event_type"] == "test_fail"
    assert events[2]["event_type"] == "deploy"


def test_log_telemetry_with_metadata(tmp_path: Path) -> None:
    """log_telemetry.py stores metadata dict correctly."""
    meta = json.dumps({"run_id": "abc123", "branch": "main"})
    subprocess.run(
        [
            sys.executable,
            _LOG_TELEMETRY,
            "--state-dir",
            str(tmp_path),
            "--event-type",
            "workflow_run",
            "--component",
            "ci",
            "--metadata",
            meta,
        ],
        check=True,
    )
    events = json.loads((tmp_path / "telemetry.json").read_text())
    assert events[0]["metadata"]["run_id"] == "abc123"


def test_log_telemetry_invalid_metadata(tmp_path: Path) -> None:
    """log_telemetry.py exits non-zero for invalid --metadata JSON."""
    result = subprocess.run(
        [
            sys.executable,
            _LOG_TELEMETRY,
            "--state-dir",
            str(tmp_path),
            "--event-type",
            "error",
            "--component",
            "api",
            "--metadata",
            "not-valid-json",
        ],
        capture_output=True,
        text=True,
    )
    assert result.returncode != 0
