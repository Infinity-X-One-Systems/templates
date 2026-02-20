"""Tests for the investor dashboard."""
from src.dashboard import InvestorDashboard, Investment


def test_add_investment_and_metrics():
    dash = InvestorDashboard()
    inv1 = Investment(name="AAPL Shares", asset_class="equity", invested_amount=10_000, current_value=12_000, entry_date="2025-01-01")
    inv2 = Investment(name="Real Estate Fund", asset_class="real_estate", invested_amount=50_000, current_value=55_000, entry_date="2025-01-01")
    dash.add_investment(inv1)
    dash.add_investment(inv2)
    metrics = dash.get_metrics()
    assert metrics.total_invested == 60_000
    assert metrics.current_value == 67_000
    assert metrics.total_return == 7_000


def test_return_percentage():
    inv = Investment(name="Test", asset_class="equity", invested_amount=1_000, current_value=1_200, entry_date="2025-01-01")
    assert abs(inv.return_pct - 20.0) < 0.01


def test_empty_portfolio():
    dash = InvestorDashboard()
    metrics = dash.get_metrics()
    assert metrics.total_invested == 0
    assert metrics.total_return_pct == 0


def test_asset_allocation():
    dash = InvestorDashboard()
    dash.add_investment(Investment(name="A", asset_class="equity", invested_amount=5000, current_value=5000, entry_date="2025-01-01"))
    dash.add_investment(Investment(name="B", asset_class="real_estate", invested_amount=5000, current_value=5000, entry_date="2025-01-01"))
    metrics = dash.get_metrics()
    assert abs(metrics.asset_allocation["equity"] - 50.0) < 0.01
    assert abs(metrics.asset_allocation["real_estate"] - 50.0) < 0.01
