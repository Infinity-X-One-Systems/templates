from __future__ import annotations
import uuid
from datetime import datetime, timezone
from typing import Any, Dict, List, Optional
from pydantic import BaseModel, Field


VALID_RATINGS = {"buy", "hold", "sell"}


class ResearchNote(BaseModel):
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    analyst_id: str
    ticker: str
    thesis: str
    target_price: float
    rating: str
    current_price: float = 0.0
    price_history: List[Dict[str, Any]] = Field(default_factory=list)
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)


class ResearchReport(BaseModel):
    note: ResearchNote
    metrics: Dict[str, Any]
    recommendation: str


class InvestmentResearchEngine:
    def __init__(self) -> None:
        self._notes: dict[str, ResearchNote] = {}

    def create_research_note(
        self,
        analyst_id: str,
        ticker: str,
        thesis: str,
        target_price: float,
        rating: str,
        current_price: float = 0.0,
    ) -> ResearchNote:
        if rating not in VALID_RATINGS:
            raise ValueError(f"Invalid rating: {rating}. Must be one of {VALID_RATINGS}")
        note = ResearchNote(
            analyst_id=analyst_id,
            ticker=ticker,
            thesis=thesis,
            target_price=target_price,
            rating=rating,
            current_price=current_price,
        )
        self._notes[note.id] = note
        return note

    def update_price_target(
        self,
        note_id: str,
        new_target: float,
        rationale: str,
    ) -> ResearchNote:
        if note_id not in self._notes:
            raise ValueError(f"Note {note_id} not found")
        note = self._notes[note_id]
        note.price_history.append({
            "old_target": note.target_price,
            "new_target": new_target,
            "rationale": rationale,
            "updated_at": datetime.now(timezone.utc).isoformat(),
        })
        note.target_price = new_target
        note.updated_at = datetime.now(timezone.utc)
        self._notes[note_id] = note
        return note

    def calculate_portfolio_alpha(
        self,
        notes: list[ResearchNote],
        market_return_pct: float,
    ) -> float:
        if not notes:
            return 0.0
        returns = []
        for note in notes:
            if note.current_price > 0:
                implied_return = (note.target_price - note.current_price) / note.current_price * 100
            else:
                implied_return = 0.0
            returns.append(implied_return)
        avg_return = sum(returns) / len(returns)
        return avg_return - market_return_pct

    def screen_opportunities(self, criteria: dict[str, Any]) -> list[ResearchNote]:
        results = list(self._notes.values())
        if "rating" in criteria:
            results = [n for n in results if n.rating == criteria["rating"]]
        if "min_target_price" in criteria:
            results = [n for n in results if n.target_price >= criteria["min_target_price"]]
        if "max_target_price" in criteria:
            results = [n for n in results if n.target_price <= criteria["max_target_price"]]
        if "ticker" in criteria:
            results = [n for n in results if n.ticker == criteria["ticker"]]
        if "analyst_id" in criteria:
            results = [n for n in results if n.analyst_id == criteria["analyst_id"]]
        return results

    def generate_research_report(self, note_id: str) -> ResearchReport:
        if note_id not in self._notes:
            raise ValueError(f"Note {note_id} not found")
        note = self._notes[note_id]
        upside = 0.0
        if note.current_price > 0:
            upside = (note.target_price - note.current_price) / note.current_price * 100
        metrics = {
            "upside_pct": round(upside, 2),
            "target_price": note.target_price,
            "current_price": note.current_price,
            "price_updates": len(note.price_history),
        }
        if upside > 15:
            recommendation = "Strong Buy"
        elif upside > 5:
            recommendation = "Buy"
        elif upside > -5:
            recommendation = "Hold"
        else:
            recommendation = "Sell"
        return ResearchReport(note=note, metrics=metrics, recommendation=recommendation)
