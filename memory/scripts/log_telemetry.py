#!/usr/bin/env python3
"""Append a telemetry event to telemetry.json.

Creates the file if it does not already exist.

Usage:
    python log_telemetry.py \\
        --state-dir /path \\
        --event-type test_pass \\
        --component backend \\
        --value 120 \\
        --unit ms \\
        --metadata '{"test": "test_api_health"}'
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


def log_telemetry(
    state_dir: Path,
    event_type: str,
    component: str,
    value: float | None,
    unit: str | None,
    metadata: dict[str, Any] | None,
) -> None:
    state_dir.mkdir(parents=True, exist_ok=True)
    telemetry_path = state_dir / "telemetry.json"

    if telemetry_path.exists():
        with telemetry_path.open() as fh:
            events: list[dict[str, Any]] = json.load(fh)
    else:
        events = []

    event: dict[str, Any] = {
        "event_id": str(uuid.uuid4()),
        "timestamp": _now_iso(),
        "event_type": event_type,
        "component": component,
    }
    if value is not None:
        event["value"] = value
    if unit is not None:
        event["unit"] = unit
    if metadata is not None:
        event["metadata"] = metadata

    events.append(event)
    _atomic_write(telemetry_path, events)


def main() -> None:
    parser = argparse.ArgumentParser(
        description="Append a telemetry event to telemetry.json."
    )
    parser.add_argument(
        "--state-dir",
        required=True,
        type=Path,
        help="Directory containing the state JSON files.",
    )
    parser.add_argument(
        "--event-type",
        required=True,
        choices=["workflow_run", "test_pass", "test_fail", "deploy", "error", "health_check"],
        help="Category of the telemetry event.",
    )
    parser.add_argument("--component", required=True, help="Component emitting the event.")
    parser.add_argument("--value", type=float, default=None, help="Numeric measurement.")
    parser.add_argument("--unit", default=None, help="Unit for --value (e.g. ms, %%).")
    parser.add_argument(
        "--metadata",
        default=None,
        help="JSON string of additional metadata key-value pairs.",
    )
    args = parser.parse_args()

    metadata: dict[str, Any] | None = None
    if args.metadata is not None:
        try:
            metadata = json.loads(args.metadata)
        except json.JSONDecodeError as exc:
            import sys
            print(f"ERROR: --metadata is not valid JSON: {exc}", file=sys.stderr)
            sys.exit(1)

    log_telemetry(
        state_dir=args.state_dir,
        event_type=args.event_type,
        component=args.component,
        value=args.value,
        unit=args.unit,
        metadata=metadata,
    )


if __name__ == "__main__":
    main()
