"""
Investor Dashboard — Infinity Template Library
Portfolio tracking, returns analysis, and investor reporting.
"""
from __future__ import annotations

from datetime import datetime, timezone
from typing import Optional
from uuid import uuid4

from pydantic import BaseModel, Field


class Investment(BaseModel):
    id: str = Field(default_factory=lambda: str(uuid4()))
    name: str
    asset_class: str  # "equity" | "real_estate" | "fixed_income" | "crypto" | "alternative"
    invested_amount: float
    current_value: float
    entry_date: str
    currency: str = "USD"

    @property
    def return_amount(self) -> float:
        return self.current_value - self.invested_amount

    @property
    def return_pct(self) -> float:
        return (self.current_value - self.invested_amount) / self.invested_amount * 100 if self.invested_amount else 0.0


class PortfolioMetrics(BaseModel):
    total_invested: float
    current_value: float
    total_return: float
    total_return_pct: float
    best_performer: Optional[str] = None
    worst_performer: Optional[str] = None
    asset_allocation: dict[str, float] = Field(default_factory=dict)


class InvestorDashboard:
    """Portfolio analytics and investor reporting."""

    def __init__(self) -> None:
        self._investments: dict[str, Investment] = {}

    def add_investment(self, inv: Investment) -> Investment:
        self._investments[inv.id] = inv
        return inv

    def update_value(self, investment_id: str, current_value: float) -> Investment:
        inv = self._investments.get(investment_id)
        if inv is None:
            raise ValueError(f"Investment {investment_id} not found")
        inv.current_value = current_value
        return inv

    def get_metrics(self) -> PortfolioMetrics:
        if not self._investments:
            return PortfolioMetrics(total_invested=0, current_value=0, total_return=0, total_return_pct=0)

        invs = list(self._investments.values())
        total_invested = sum(i.invested_amount for i in invs)
        current_value = sum(i.current_value for i in invs)
        total_return = current_value - total_invested
        total_return_pct = (total_return / total_invested * 100) if total_invested else 0.0

        best = max(invs, key=lambda i: i.return_pct)
        worst = min(invs, key=lambda i: i.return_pct)

        # Asset allocation
        allocation: dict[str, float] = {}
        for inv in invs:
            allocation[inv.asset_class] = allocation.get(inv.asset_class, 0) + inv.current_value
        if current_value > 0:
            allocation = {k: v / current_value * 100 for k, v in allocation.items()}

        return PortfolioMetrics(
            total_invested=round(total_invested, 2),
            current_value=round(current_value, 2),
            total_return=round(total_return, 2),
            total_return_pct=round(total_return_pct, 2),
            best_performer=best.name,
            worst_performer=worst.name,
            asset_allocation=allocation,
        )
