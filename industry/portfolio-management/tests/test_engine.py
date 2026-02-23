from src.engine import PortfolioManagementEngine


def test_create_portfolio():
    engine = PortfolioManagementEngine()
    p = engine.create_portfolio("Growth Fund", "manager-1", "growth", "medium", 12.0)
    assert p.name == "Growth Fund"
    assert p.target_return_pct == 12.0


def test_add_holding():
    engine = PortfolioManagementEngine()
    p = engine.create_portfolio("Tech Fund", "mgr-1", "tech", "high", 15.0)
    h = engine.add_holding(p.id, "AAPL", 100, 150.0, 180.0)
    assert h.ticker == "AAPL"
    assert h.current_value == 18000.0


def test_rebalance():
    engine = PortfolioManagementEngine()
    p = engine.create_portfolio("Balanced Fund", "mgr-2", "balanced", "low", 8.0)
    engine.add_holding(p.id, "AAPL", 100, 150.0, 200.0)
    engine.add_holding(p.id, "GOOG", 50, 100.0, 120.0)
    order = engine.rebalance(p.id, {"AAPL": 0.7, "GOOG": 0.3})
    assert isinstance(order.buys, list)
    assert isinstance(order.sells, list)


def test_generate_client_report():
    engine = PortfolioManagementEngine()
    p = engine.create_portfolio("Income Fund", "mgr-3", "income", "low", 6.0)
    engine.add_holding(p.id, "MSFT", 50, 300.0, 350.0)
    engine.add_holding(p.id, "AMZN", 10, 3000.0, 3500.0)
    report = engine.generate_client_report(p.id)
    assert report.total_value == 52500.0
    assert report.total_gain_loss == 7500.0
    assert len(report.holdings) == 2
