#!/usr/bin/env python3
"""Rehydrate system memory by loading and validating all state files.

Reads system_state.json, decision_log.json, architecture_map.json, and
telemetry.json from --state-dir, validates each against its JSON Schema,
and writes a consolidated context dict as JSON to --output (or stdout).

Exit code is always 0; missing files are reported as warnings.
"""

from __future__ import annotations

import argparse
import json
import sys
import warnings
from pathlib import Path
from typing import Any

try:
    import jsonschema
    from jsonschema import validate, ValidationError
except ImportError:  # pragma: no cover
    print("ERROR: jsonschema is required. Run: pip install jsonschema", file=sys.stderr)
    sys.exit(1)

# Resolve schema directory relative to this script.
_SCHEMA_DIR = Path(__file__).resolve().parent.parent / "schemas"

_STATE_FILES: dict[str, str] = {
    "system_state": "system_state.json",
    "decision_log": "decision_log.json",
    "architecture_map": "architecture_map.json",
    "telemetry": "telemetry.json",
}

_SCHEMA_FILES: dict[str, str] = {
    "system_state": "system_state.schema.json",
    "decision_log": "decision_log.schema.json",
    "architecture_map": "architecture_map.schema.json",
    "telemetry": "telemetry.schema.json",
}


def _load_schema(key: str) -> dict[str, Any]:
    schema_path = _SCHEMA_DIR / _SCHEMA_FILES[key]
    with schema_path.open() as fh:
        return json.load(fh)


def _load_and_validate(
    state_dir: Path,
    key: str,
    warn_list: list[str],
) -> Any:
    file_path = state_dir / _STATE_FILES[key]
    if not file_path.exists():
        warn_list.append(f"Missing state file: {file_path}")
        return None

    with file_path.open() as fh:
        data = json.load(fh)

    schema = _load_schema(key)
    try:
        validate(instance=data, schema=schema)
    except ValidationError as exc:
        warn_list.append(f"Validation warning for {file_path.name}: {exc.message}")

    return data


def rehydrate(state_dir: Path) -> dict[str, Any]:
    """Load all state files and return a consolidated context dict."""
    warn_list: list[str] = []
    context: dict[str, Any] = {"warnings": warn_list}

    for key in _STATE_FILES:
        context[key] = _load_and_validate(state_dir, key, warn_list)

    return context


def main() -> None:
    parser = argparse.ArgumentParser(
        description="Rehydrate system memory from state files."
    )
    parser.add_argument(
        "--state-dir",
        required=True,
        type=Path,
        help="Directory containing the state JSON files.",
    )
    parser.add_argument(
        "--output",
        type=Path,
        default=None,
        help="Path to write the consolidated context JSON. Defaults to stdout.",
    )
    args = parser.parse_args()

    if not args.state_dir.is_dir():
        print(
            f"WARNING: state-dir does not exist: {args.state_dir}",
            file=sys.stderr,
        )

    context = rehydrate(args.state_dir)

    for warning in context.get("warnings", []):
        print(f"WARNING: {warning}", file=sys.stderr)

    output_json = json.dumps(context, indent=2)

    if args.output:
        args.output.parent.mkdir(parents=True, exist_ok=True)
        args.output.write_text(output_json)
    else:
        print(output_json)


if __name__ == "__main__":
    main()
