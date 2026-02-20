# Memory & Rehydration System

The Memory & Rehydration system implements the **repo-backed memory principle** for the Infinity Template Library: every major action writes to memory, and every workflow begins by rehydrating from that memory.

---

## Directory Structure

```
memory/
├── schemas/                    # JSON Schemas for all state files
│   ├── system_state.schema.json
│   ├── decision_log.schema.json
│   ├── architecture_map.schema.json
│   └── telemetry.schema.json
├── scripts/                    # CLI scripts for reading/writing memory
│   ├── rehydrate.py
│   ├── write_state.py
│   ├── log_decision.py
│   └── log_telemetry.py
├── tests/
│   ├── __init__.py
│   └── test_memory.py
├── requirements.txt
├── requirements-dev.txt
├── pytest.ini
└── README.md
```

---

## Memory Interface Contract

All state files live in a single **state directory** (referred to as `STATE_DIR` below). Scripts accept `--state-dir` to point at this directory. Missing files are treated as warnings, not hard errors, so workflows always start cleanly even on first run.

### Atomic Writes

Every write script uses a write-to-`.tmp`-then-`os.replace` pattern to ensure state files are never left in a partially-written state.

---

## Schema Files

### `system_state.schema.json`

Tracks the overall health and lifecycle of the system.

| Field | Type | Description |
|---|---|---|
| `manifest_version` | string | Schema version |
| `system_name` | string | System identifier |
| `org` | string | Owning organisation |
| `phase` | enum | `planning` / `building` / `testing` / `deployed` |
| `components_status` | object | Map of component → status string |
| `last_action` | string | Human-readable last action |
| `last_action_at` | string (date-time) | ISO-8601 timestamp |
| `health_score` | integer 0–100 | Aggregate health score |
| `errors` | string[] | Current errors |
| `warnings` | string[] | Current warnings |

### `decision_log.schema.json`

Append-only log of architectural and operational decisions.

| Field | Type | Description |
|---|---|---|
| `id` | string | UUID |
| `timestamp` | string (date-time) | When the decision was made |
| `decision_type` | string | Category (e.g. `architecture`, `tooling`) |
| `description` | string | What was decided |
| `rationale` | string | Why |
| `made_by` | enum | `human` or `agent` |
| `outcome` | string (optional) | Observed/expected outcome |
| `related_components` | string[] | Affected components |

### `architecture_map.schema.json`

Snapshot of the system's component topology.

| Field | Type | Description |
|---|---|---|
| `system_name` | string | System identifier |
| `components` | array | See below |
| `dependency_graph` | object | Adjacency list (component → [deps]) |
| `last_updated` | string (date-time) | Last map update |

Each component entry: `name`, `type`, `path`, `status`, `dependencies` (string[]), `health` (0–100).

### `telemetry.schema.json`

Time-series telemetry events.

| Field | Type | Description |
|---|---|---|
| `event_id` | string | UUID |
| `timestamp` | string (date-time) | When the event occurred |
| `event_type` | enum | `workflow_run` / `test_pass` / `test_fail` / `deploy` / `error` / `health_check` |
| `component` | string | Emitting component |
| `value` | number (optional) | Numeric measurement |
| `unit` | string (optional) | Unit (e.g. `ms`, `%`) |
| `metadata` | object (optional) | Arbitrary key-value context |

---

## Script Usage

### Install dependencies

```bash
pip install -r memory/requirements.txt
```

### `rehydrate.py` — Load and validate all state files

```bash
python memory/scripts/rehydrate.py \
    --state-dir /path/to/state \
    --output /path/to/context.json   # optional; defaults to stdout
```

- Validates each file against its JSON Schema.
- Outputs a consolidated JSON object with keys `system_state`, `decision_log`, `architecture_map`, `telemetry`, and `warnings`.
- Always exits with code `0`; missing or invalid files are reported as warnings on stderr.

### `write_state.py` — Update `system_state.json`

```bash
python memory/scripts/write_state.py \
    --state-dir /path/to/state \
    --phase building \
    --action "scaffold_backend" \
    --health-score 85 \
    --component api \
    --status healthy \
    --system-name my-system
```

All fields are optional except `--state-dir`. Creates the file with defaults if it does not exist.

### `log_decision.py` — Append to `decision_log.json`

```bash
python memory/scripts/log_decision.py \
    --state-dir /path/to/state \
    --type architecture \
    --description "Use PostgreSQL for persistence" \
    --rationale "ACID compliance required" \
    --made-by human \
    --component backend \
    --component frontend \
    --outcome "Adopted in v1"
```

`--component` may be repeated. `--outcome` is optional.

### `log_telemetry.py` — Append to `telemetry.json`

```bash
python memory/scripts/log_telemetry.py \
    --state-dir /path/to/state \
    --event-type test_pass \
    --component backend \
    --value 120 \
    --unit ms \
    --metadata '{"test": "test_api_health", "run_id": "abc123"}'
```

`--value`, `--unit`, and `--metadata` are optional. `--metadata` must be a valid JSON object string.

---

## Running Tests

```bash
pip install -r memory/requirements.txt -r memory/requirements-dev.txt
cd memory
pytest
```

Tests use `tmp_path` fixtures and invoke scripts via `subprocess` to validate real CLI behaviour.

---

## Workflow Integration

A typical workflow preamble looks like:

```bash
# 1. Rehydrate context at the start of every workflow
python memory/scripts/rehydrate.py --state-dir .memory --output .memory/context.json

# 2. ... do work ...

# 3. Write updated state after each significant action
python memory/scripts/write_state.py --state-dir .memory --phase building --action "run_tests" --health-score 95

# 4. Log the decision that drove the action
python memory/scripts/log_decision.py --state-dir .memory \
    --type process --description "Enabled unit tests" \
    --rationale "Quality gate" --made-by agent

# 5. Emit telemetry
python memory/scripts/log_telemetry.py --state-dir .memory \
    --event-type test_pass --component backend --value 42 --unit ms
```
