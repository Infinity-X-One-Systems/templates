#!/usr/bin/env python3
"""Write or update system_state.json atomically.

Reads an existing system_state.json (or creates a default) from --state-dir,
updates the specified fields, then writes back atomically via a .tmp file rename.

Usage:
    python write_state.py --state-dir /path \\
        --phase building \\
        --action "scaffold_backend" \\
        --health-score 85
"""

from __future__ import annotations

import argparse
import json
import os
import sys
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

_DEFAULT_STATE: dict[str, Any] = {
    "manifest_version": "1.0.0",
    "system_name": "infinity-template-library",
    "org": "unknown",
    "phase": "planning",
    "components_status": {},
    "last_action": "initialized",
    "last_action_at": "",
    "health_score": 100,
    "errors": [],
    "warnings": [],
}


def _now_iso() -> str:
    return datetime.now(tz=timezone.utc).isoformat()


def _atomic_write(path: Path, data: dict[str, Any]) -> None:
    tmp_path = path.with_suffix(".tmp")
    tmp_path.write_text(json.dumps(data, indent=2))
    os.replace(tmp_path, path)


def load_state(state_dir: Path) -> dict[str, Any]:
    state_path = state_dir / "system_state.json"
    if state_path.exists():
        with state_path.open() as fh:
            return json.load(fh)
    state = dict(_DEFAULT_STATE)
    state["last_action_at"] = _now_iso()
    return state



def write_state(
    state_dir: Path,
    system_name: str | None,
    phase: str | None,
    component: str | None,
    status: str | None,
    action: str | None,
    health_score: int | None,
) -> None:
    state_dir.mkdir(parents=True, exist_ok=True)
    state = load_state(state_dir)

    if system_name is not None:
        state["system_name"] = system_name
    if phase is not None:
        state["phase"] = phase
    if component is not None and status is not None:
        if "components_status" not in state:
            state["components_status"] = {}
        state["components_status"][component] = status
    if action is not None:
        state["last_action"] = action
    if health_score is not None:
        state["health_score"] = health_score

    state["last_action_at"] = _now_iso()

    _atomic_write(state_dir / "system_state.json", state)


def main() -> None:
    parser = argparse.ArgumentParser(
        description="Update system_state.json with current system information."
    )
    parser.add_argument(
        "--state-dir",
        required=True,
        type=Path,
        help="Directory containing the state JSON files.",
    )
    parser.add_argument("--system-name", default=None, help="System name to set.")
    parser.add_argument(
        "--phase",
        default=None,
        choices=["planning", "building", "testing", "deployed"],
        help="Lifecycle phase to set.",
    )
    parser.add_argument(
        "--component", default=None, help="Component name (used with --status)."
    )
    parser.add_argument(
        "--status", default=None, help="Status to assign to --component."
    )
    parser.add_argument("--action", default=None, help="Description of the last action.")
    parser.add_argument(
        "--health-score",
        type=int,
        default=None,
        metavar="0-100",
        help="Overall system health score (0-100).",
    )
    args = parser.parse_args()

    if args.health_score is not None and not (0 <= args.health_score <= 100):
        print("ERROR: --health-score must be between 0 and 100.", file=sys.stderr)
        sys.exit(1)

    write_state(
        state_dir=args.state_dir,
        system_name=args.system_name,
        phase=args.phase,
        component=args.component,
        status=args.status,
        action=args.action,
        health_score=args.health_score,
    )


if __name__ == "__main__":
    main()
