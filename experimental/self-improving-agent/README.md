# Self-Improving Agent

An agent that tracks its own performance and automatically writes improvements to its own strategy and prompt. This is the foundation of autonomous capability growth.

## Concept

Most AI agents are static — they don't change based on how well they're performing. The Self-Improving Agent closes that loop:

1. **Record** — After each task, record a performance score (0.0–1.0) along a dimension (accuracy, speed, cost, user_satisfaction)
2. **Analyze** — After enough tasks, analyze performance by dimension and identify the weakest area
3. **Propose** — Generate a targeted improvement proposal for the weakest dimension
4. **Apply** — Apply the improvement, creating a new versioned agent
5. **Rollback** — If the new version is worse, roll back to the previous version

## Usage

```python
from src.agent import SelfImprovingAgent

agent = SelfImprovingAgent(
    name="research-agent",
    initial_prompt="You are a research assistant. Be thorough.",
    initial_strategy="default",
)

# Record task performance
agent.record_performance("task-001", score=0.55, dimension="accuracy", details="Missed two citations")
agent.record_performance("task-002", score=0.60, dimension="accuracy", details="One hallucination detected")
agent.record_performance("task-003", score=0.50, dimension="accuracy", details="Outdated sources used")

# Analyze and get proposals
proposals = agent.analyze_and_propose()
for p in proposals:
    print(f"Proposal: {p.proposed_value} — {p.expected_improvement}")

# Apply the best proposal (after human review)
new_version = agent.apply_improvement(proposals[0].proposal_id, new_prompt="You are a research assistant. Always cite primary sources.")
print(f"Upgraded to version {new_version.version}")

# Rollback if needed
agent.rollback()
```

## Governance

- Improvements are **proposed**, not auto-applied — the caller decides when to invoke `apply_improvement()`
- Version history is maintained for full auditability and rollback
- Scores must be in `[0.0, 1.0]` — invalid scores raise `ValueError`

## Running Tests

```bash
pip install -r requirements.txt -r requirements-dev.txt
pytest
```

## Docker

```bash
docker build -t self-improving-agent .
docker run self-improving-agent
```
