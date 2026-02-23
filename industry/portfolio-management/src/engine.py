from __future__ import annotations
import uuid
from datetime import datetime, timezone
from typing import Any, Dict, List, Optional
from pydantic import BaseModel, Field


class ManagedPortfolio(BaseModel):
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    name: str
    manager_id: str
    strategy: str
    risk_level: str
    target_return_pct: float
    created_at: datetime = Field(default_factory=datetime.utcnow)


class Holding(BaseModel):
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    portfolio_id: str
    ticker: str
    shares: float
    purchase_price: float
    current_price: float
    added_at: datetime = Field(default_factory=datetime.utcnow)

    @property
    def current_value(self) -> float:
        return self.shares * self.current_price

    @property
    def gain_loss(self) -> float:
        return (self.current_price - self.purchase_price) * self.shares


class RebalanceOrder(BaseModel):
    portfolio_id: str
    buys: List[Dict[str, Any]]
    sells: List[Dict[str, Any]]
    generated_at: datetime = Field(default_factory=datetime.utcnow)


class RiskMetrics(BaseModel):
    portfolio_id: str
    volatility_score: float
    beta: float
    sharpe_ratio_estimate: float


class Attribution(BaseModel):
    ticker: str
    weight: float
    gain_loss: float
    contribution: float


class ClientReport(BaseModel):
    portfolio_id: str
    total_value: float
    total_gain_loss: float
    return_pct: float
    holdings: List[Holding]
    attribution: List[Attribution]
    generated_at: datetime = Field(default_factory=datetime.utcnow)


class PortfolioManagementEngine:
    def __init__(self) -> None:
        self._portfolios: dict[str, ManagedPortfolio] = {}
        self._holdings: list[Holding] = []

    def create_portfolio(
        self,
        name: str,
        manager_id: str,
        strategy: str,
        risk_level: str,
        target_return_pct: float,
    ) -> ManagedPortfolio:
        p = ManagedPortfolio(
            name=name,
            manager_id=manager_id,
            strategy=strategy,
            risk_level=risk_level,
            target_return_pct=target_return_pct,
        )
        self._portfolios[p.id] = p
        return p

    def add_holding(
        self,
        portfolio_id: str,
        ticker: str,
        shares: float,
        purchase_price: float,
        current_price: float,
    ) -> Holding:
        if portfolio_id not in self._portfolios:
            raise ValueError(f"Portfolio {portfolio_id} not found")
        h = Holding(
            portfolio_id=portfolio_id,
            ticker=ticker,
            shares=shares,
            purchase_price=purchase_price,
            current_price=current_price,
        )
        self._holdings.append(h)
        return h

    def rebalance(
        self,
        portfolio_id: str,
        target_allocations: dict[str, float],
    ) -> RebalanceOrder:
        if portfolio_id not in self._portfolios:
            raise ValueError(f"Portfolio {portfolio_id} not found")
        holdings = [h for h in self._holdings if h.portfolio_id == portfolio_id]
        total_value = sum(h.current_value for h in holdings)
        current_alloc = {h.ticker: h.current_value / total_value if total_value else 0 for h in holdings}
        buys = []
        sells = []
        for ticker, target_pct in target_allocations.items():
            current_pct = current_alloc.get(ticker, 0.0)
            diff_pct = target_pct - current_pct
            diff_value = diff_pct * total_value
            if diff_value > 0:
                buys.append({"ticker": ticker, "value": round(diff_value, 2), "target_pct": target_pct})
            elif diff_value < 0:
                sells.append({"ticker": ticker, "value": round(abs(diff_value), 2), "target_pct": target_pct})
        return RebalanceOrder(portfolio_id=portfolio_id, buys=buys, sells=sells)

    def calculate_risk_metrics(self, portfolio_id: str) -> RiskMetrics:
        if portfolio_id not in self._portfolios:
            raise ValueError(f"Portfolio {portfolio_id} not found")
        holdings = [h for h in self._holdings if h.portfolio_id == portfolio_id]
        if not holdings:
            return RiskMetrics(
                portfolio_id=portfolio_id,
                volatility_score=0.0,
                beta=1.0,
                sharpe_ratio_estimate=0.0,
            )
        returns = [(h.current_price - h.purchase_price) / h.purchase_price for h in holdings]
        avg_return = sum(returns) / len(returns)
        variance = sum((r - avg_return) ** 2 for r in returns) / len(returns)
        volatility = variance ** 0.5
        beta = 1.0 + (avg_return - 0.08)
        risk_free_rate = 0.04
        sharpe = (avg_return - risk_free_rate) / volatility if volatility > 0 else 0.0
        return RiskMetrics(
            portfolio_id=portfolio_id,
            volatility_score=round(volatility, 4),
            beta=round(beta, 4),
            sharpe_ratio_estimate=round(sharpe, 4),
        )

    def generate_client_report(self, portfolio_id: str) -> ClientReport:
        if portfolio_id not in self._portfolios:
            raise ValueError(f"Portfolio {portfolio_id} not found")
        holdings = [h for h in self._holdings if h.portfolio_id == portfolio_id]
        total_value = sum(h.current_value for h in holdings)
        total_cost = sum(h.shares * h.purchase_price for h in holdings)
        total_gain_loss = total_value - total_cost
        return_pct = (total_gain_loss / total_cost * 100) if total_cost else 0.0
        attribution = []
        for h in holdings:
            weight = h.current_value / total_value if total_value else 0.0
            contribution = weight * (h.current_price - h.purchase_price) / h.purchase_price if h.purchase_price else 0.0
            attribution.append(Attribution(
                ticker=h.ticker,
                weight=round(weight, 4),
                gain_loss=round(h.gain_loss, 2),
                contribution=round(contribution, 4),
            ))
        return ClientReport(
            portfolio_id=portfolio_id,
            total_value=round(total_value, 2),
            total_gain_loss=round(total_gain_loss, 2),
            return_pct=round(return_pct, 2),
            holdings=holdings,
            attribution=attribution,
        )
