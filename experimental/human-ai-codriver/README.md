# Human-AI Co-Driver

A new interaction paradigm where a human and AI share a steering wheel — the human sets direction and constraints, the AI handles execution, and both learn from each other over time.

## Concept

Traditional AI assistants either require constant human direction (chatbots) or operate fully autonomously (risky). The Co-Driver model strikes a balance:

| Role | Responsibility |
|------|---------------|
| **Human** | Goals, constraints, approvals, corrections, vetoes |
| **AI** | Execution, proposals, analysis, memory, suggestions |
| **Both** | Shared context, learnings, iterative improvement |

## Usage

```python
from src.codriver import HumanAICoDriver

driver = HumanAICoDriver()

# Human sets the goal and guardrails
driver.set_intent(
    goal="Deploy new microservice to production",
    constraints=["zero downtime", "rollback within 60s if health check fails"],
    blocked_actions=["delete production database", "disable monitoring"],
)

# AI proposes actions
proposal = driver.ai_propose(
    action="Run smoke tests in staging",
    rationale="Validates service before production traffic",
    estimated_impact="Catch regressions early",
    risk_level="low",
    reversible=True,
)

# Low-risk proposals auto-approve
decision = driver.auto_approve(proposal.proposal_id)

# High-risk proposals require human sign-off
risky = driver.ai_propose(
    action="Switch production traffic",
    rationale="All tests passed",
    estimated_impact="Users routed to new service",
    risk_level="high",
    reversible=True,
)
driver.human_decide(risky.proposal_id, approved=True, comment="Green light")

# Both sides capture learnings
driver.learn("Staging smoke tests caught the missing env var — always run them first")

print(driver.get_session_summary())
```

## Governance

- **High-risk** or **irreversible** actions always require `human_decide()` — never auto-approved.
- Blocked actions (set in `set_intent`) force `requires_approval=True` regardless of risk level.
- All decisions are recorded in `SharedContext` for audit and replay.

## Running Tests

```bash
pip install -r requirements.txt -r requirements-dev.txt
pytest
```

## Docker

```bash
docker build -t human-ai-codriver .
docker run human-ai-codriver
```
