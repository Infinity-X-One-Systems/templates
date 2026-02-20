#!/usr/bin/env python3
"""Append a decision entry to decision_log.json.

Creates the file if it does not already exist.

Usage:
    python log_decision.py \\
        --state-dir /path \\
        --type architecture \\
        --description "Use PostgreSQL for persistence" \\
        --rationale "ACID compliance required" \\
        --made-by human \\
        --component backend
"""

from __future__ import annotations

import argparse
import json
import os
import uuid
from datetime import datetime, timezone
from pathlib import Path
from typing import Any


def _now_iso() -> str:
    return datetime.now(tz=timezone.utc).isoformat()


def _atomic_write(path: Path, data: list[Any]) -> None:
    tmp_path = path.with_suffix(".tmp")
    tmp_path.write_text(json.dumps(data, indent=2))
    os.replace(tmp_path, path)


def log_decision(
    state_dir: Path,
    decision_type: str,
    description: str,
    rationale: str,
    made_by: str,
    outcome: str | None,
    related_components: list[str],
) -> None:
    state_dir.mkdir(parents=True, exist_ok=True)
    log_path = state_dir / "decision_log.json"

    if log_path.exists():
        with log_path.open() as fh:
            log: list[dict[str, Any]] = json.load(fh)
    else:
        log = []

    entry: dict[str, Any] = {
        "id": str(uuid.uuid4()),
        "timestamp": _now_iso(),
        "decision_type": decision_type,
        "description": description,
        "rationale": rationale,
        "made_by": made_by,
        "related_components": related_components,
    }
    if outcome is not None:
        entry["outcome"] = outcome

    log.append(entry)
    _atomic_write(log_path, log)


def main() -> None:
    parser = argparse.ArgumentParser(
        description="Append a decision to decision_log.json."
    )
    parser.add_argument(
        "--state-dir",
        required=True,
        type=Path,
        help="Directory containing the state JSON files.",
    )
    parser.add_argument("--type", required=True, dest="decision_type", help="Decision type.")
    parser.add_argument("--description", required=True, help="What was decided.")
    parser.add_argument("--rationale", required=True, help="Why this decision was made.")
    parser.add_argument(
        "--made-by",
        required=True,
        choices=["human", "agent"],
        help="Whether the decision was made by a human or an AI agent.",
    )
    parser.add_argument("--outcome", default=None, help="Observed or expected outcome.")
    parser.add_argument(
        "--component",
        action="append",
        dest="components",
        default=[],
        metavar="COMPONENT",
        help="Related component (may be repeated).",
    )
    args = parser.parse_args()

    log_decision(
        state_dir=args.state_dir,
        decision_type=args.decision_type,
        description=args.description,
        rationale=args.rationale,
        made_by=args.made_by,
        outcome=args.outcome,
        related_components=args.components,
    )


if __name__ == "__main__":
    main()
