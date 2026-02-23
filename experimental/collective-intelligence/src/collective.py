"""
Collective Intelligence Template
=================================
A swarm of specialized agents that vote, deliberate, and synthesize
a collective answer that exceeds individual agent capability.
This enables distributed reasoning, error correction, and emergent insight.
"""
from pydantic import BaseModel, Field
from typing import Any, Optional
from datetime import datetime, timezone
from enum import Enum
import uuid


class AgentRole(str, Enum):
    ANALYST = "analyst"
    CRITIC = "critic"
    SYNTHESIZER = "synthesizer"
    DEVIL_ADVOCATE = "devil_advocate"
    DOMAIN_EXPERT = "domain_expert"


class AgentOpinion(BaseModel):
    agent_id: str
    agent_role: AgentRole
    answer: Any
    confidence: float  # 0.0-1.0
    reasoning: str
    vote: Optional[str] = None  # for voting rounds
    timestamp: str = Field(default_factory=lambda: datetime.now(timezone.utc).isoformat())


class DeliberationRound(BaseModel):
    round_id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    round_number: int
    opinions: list[AgentOpinion] = Field(default_factory=list)
    consensus_reached: bool = False
    consensus_answer: Optional[Any] = None


class CollectiveDecision(BaseModel):
    decision_id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    question: str
    rounds: list[DeliberationRound] = Field(default_factory=list)
    final_answer: Optional[Any] = None
    confidence: float = 0.0
    dissenting_views: list[str] = Field(default_factory=list)
    timestamp: str = Field(default_factory=lambda: datetime.now(timezone.utc).isoformat())


class CollectiveAgent(BaseModel):
    agent_id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    name: str
    role: AgentRole
    specialization: str
    weight: float = 1.0  # voting weight, adjusted by track record


class CollectiveIntelligence:
    """
    Collective of specialized agents that reach consensus through deliberation.
    Consensus threshold: 70% weighted agreement.
    """

    CONSENSUS_THRESHOLD = 0.70
    MAX_ROUNDS = 3

    def __init__(self):
        self.agents: list[CollectiveAgent] = []
        self.decisions: list[CollectiveDecision] = []

    def add_agent(self, name: str, role: AgentRole, specialization: str, weight: float = 1.0) -> CollectiveAgent:
        agent = CollectiveAgent(name=name, role=role, specialization=specialization, weight=weight)
        self.agents.append(agent)
        return agent

    def submit_opinion(
        self,
        decision: CollectiveDecision,
        round_number: int,
        agent_id: str,
        answer: Any,
        confidence: float,
        reasoning: str,
    ) -> AgentOpinion:
        agent = next((a for a in self.agents if a.agent_id == agent_id), None)
        if not agent:
            raise ValueError(f"Agent {agent_id} not registered in collective")
        opinion = AgentOpinion(
            agent_id=agent_id,
            agent_role=agent.role,
            answer=answer,
            confidence=confidence,
            reasoning=reasoning,
        )
        # Ensure enough rounds exist
        while len(decision.rounds) < round_number:
            decision.rounds.append(DeliberationRound(round_number=len(decision.rounds) + 1))
        decision.rounds[round_number - 1].opinions.append(opinion)
        return opinion

    def check_consensus(self, decision: CollectiveDecision, round_number: int) -> bool:
        """Check if the current round has reached consensus by weighted voting."""
        if round_number > len(decision.rounds):
            return False
        rnd = decision.rounds[round_number - 1]
        if not rnd.opinions:
            return False
        vote_weights: dict[str, float] = {}
        total_weight = 0.0
        for opinion in rnd.opinions:
            agent = next((a for a in self.agents if a.agent_id == opinion.agent_id), None)
            weight = (agent.weight if agent else 1.0) * opinion.confidence
            key = str(opinion.answer)
            vote_weights[key] = vote_weights.get(key, 0.0) + weight
            total_weight += weight
        if total_weight == 0:
            return False
        top_answer = max(vote_weights, key=lambda k: vote_weights[k])
        top_pct = vote_weights[top_answer] / total_weight
        if top_pct >= self.CONSENSUS_THRESHOLD:
            rnd.consensus_reached = True
            rnd.consensus_answer = top_answer
            decision.final_answer = top_answer
            decision.confidence = top_pct
            decision.dissenting_views = [
                o.reasoning for o in rnd.opinions if str(o.answer) != top_answer
            ]
            return True
        return False

    def deliberate(self, question: str, opinion_fn) -> CollectiveDecision:
        """
        Run a full deliberation cycle.
        opinion_fn(agent, question, round_num, prior_opinions) -> (answer, confidence, reasoning)
        """
        decision = CollectiveDecision(question=question)
        self.decisions.append(decision)
        for round_num in range(1, self.MAX_ROUNDS + 1):
            prior = decision.rounds[-1].opinions if decision.rounds else []
            for agent in self.agents:
                answer, confidence, reasoning = opinion_fn(agent, question, round_num, prior)
                self.submit_opinion(decision, round_num, agent.agent_id, answer, confidence, reasoning)
            if self.check_consensus(decision, round_num):
                break
        # If no consensus, synthesizer has final say
        if decision.final_answer is None and decision.rounds:
            last_round = decision.rounds[-1]
            synthesizer_opinion = next(
                (o for o in last_round.opinions if o.agent_role == AgentRole.SYNTHESIZER), None
            )
            if synthesizer_opinion:
                decision.final_answer = synthesizer_opinion.answer
                decision.confidence = synthesizer_opinion.confidence
        return decision
