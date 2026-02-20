# Autonomous AI System Templates

This category contains templates for building self-running, goal-directed AI agents with built-in governance controls.

## Templates

- **autonomous-loop** — An OODA (Observe → Orient → Decide → Act) agent loop that executes tasks autonomously until a goal is achieved or governance limits (budget, iterations, time) are exceeded.

## Usage

Each template is self-contained with `src/`, `tests/`, `requirements.txt`, and a `Dockerfile`. Install dependencies with `pip install -r requirements.txt` and run tests with `pytest`.

## Design Principles

- Hard governance limits: cost budget, iteration cap, and irreversible-action gating.
- Human-in-the-loop escalation when safety thresholds are reached.
- Pydantic models for all state, observations, and actions.
- Composable with `memory/` and `connectors/` modules from this repository.
