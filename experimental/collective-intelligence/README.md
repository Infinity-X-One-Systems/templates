# Collective Intelligence

A swarm of specialized agents that vote, deliberate, and synthesize a collective answer exceeding what any individual agent could produce. This template enables distributed reasoning, error correction, and emergent insight.

## Concept

| Problem | Solution |
|---------|----------|
| Single AI can hallucinate | Multiple agents cross-check each other |
| One perspective misses nuance | Role diversity (Analyst, Critic, Synthesizer, Devil's Advocate, Domain Expert) |
| No confidence signal | Weighted voting produces a calibrated confidence score |
| Gridlock | Synthesizer holds tiebreaker after MAX_ROUNDS |

## Deliberation Protocol

1. **Round 1** — Each agent submits an independent opinion
2. **Check** — If ≥70% weighted votes agree → consensus reached, done
3. **Round 2** — Agents see prior opinions and can revise
4. **Round 3** — Final round; if still no consensus, Synthesizer has final say

## Usage

```python
from src.collective import CollectiveIntelligence, AgentRole

ci = CollectiveIntelligence()

# Assemble the collective
ci.add_agent("Data Analyst", AgentRole.ANALYST, "quantitative analysis", weight=1.0)
ci.add_agent("Domain Expert", AgentRole.DOMAIN_EXPERT, "healthcare", weight=1.5)
ci.add_agent("Devil's Advocate", AgentRole.DEVIL_ADVOCATE, "risk assessment", weight=1.0)
ci.add_agent("Synthesizer", AgentRole.SYNTHESIZER, "integration", weight=1.2)

# Define how each agent forms opinions (plug in your LLM calls here)
def opinion_fn(agent, question, round_num, prior_opinions):
    # Call your LLM with agent's role + specialization as system prompt
    answer = call_llm(agent.role, agent.specialization, question, prior_opinions)
    return answer, 0.85, "Reasoning here..."

# Deliberate
decision = ci.deliberate("Should we launch feature X this week?", opinion_fn)

print(f"Decision: {decision.final_answer} (confidence: {decision.confidence:.0%})")
print(f"Dissenting views: {decision.dissenting_views}")
```

## Governance

- Consensus requires **70% weighted agreement** — individual agents cannot override the collective
- Weights reflect agent track records and can be adjusted over time
- All opinions, rounds, and dissenting views are recorded for audit

## Running Tests

```bash
pip install -r requirements.txt -r requirements-dev.txt
pytest
```

## Docker

```bash
docker build -t collective-intelligence .
docker run collective-intelligence
```
