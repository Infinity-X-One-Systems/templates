# Portfolio Management Engine

A production-grade Python module for managing investment portfolios including holdings, rebalancing, risk metrics, and client reporting.

## Features
- Create managed portfolios with strategy and risk parameters
- Add and track holdings with purchase/current prices
- Generate rebalance orders based on target allocations
- Calculate risk metrics (volatility, beta, Sharpe ratio estimate)
- Produce client reports with performance attribution

## Usage
```python
from src.engine import PortfolioManagementEngine

engine = PortfolioManagementEngine()
portfolio = engine.create_portfolio("Growth Fund", "manager-1", "growth", "medium", 12.0)
engine.add_holding(portfolio.id, "AAPL", 100, 150.0, 180.0)
report = engine.generate_client_report(portfolio.id)
risk = engine.calculate_risk_metrics(portfolio.id)
```
