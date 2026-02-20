from src.engine import InvestmentResearchEngine
import pytest


def test_create_research_note():
    engine = InvestmentResearchEngine()
    note = engine.create_research_note("analyst-1", "AAPL", "Strong iPhone cycle", 200.0, "buy", current_price=150.0)
    assert note.ticker == "AAPL"
    assert note.rating == "buy"
    assert note.target_price == 200.0


def test_update_price_target():
    engine = InvestmentResearchEngine()
    note = engine.create_research_note("analyst-2", "GOOG", "AI growth", 180.0, "buy", current_price=140.0)
    updated = engine.update_price_target(note.id, 195.0, "Better AI monetization")
    assert updated.target_price == 195.0
    assert len(updated.price_history) == 1


def test_screen_opportunities():
    engine = InvestmentResearchEngine()
    engine.create_research_note("a1", "MSFT", "Cloud growth", 400.0, "buy", current_price=350.0)
    engine.create_research_note("a1", "META", "Ad recovery", 500.0, "hold", current_price=480.0)
    buys = engine.screen_opportunities({"rating": "buy"})
    assert len(buys) == 1
    assert buys[0].ticker == "MSFT"


def test_generate_research_report():
    engine = InvestmentResearchEngine()
    note = engine.create_research_note("analyst-3", "NVDA", "GPU dominance", 1000.0, "buy", current_price=800.0)
    report = engine.generate_research_report(note.id)
    assert report.note.ticker == "NVDA"
    assert report.metrics["upside_pct"] == 25.0
    assert "Buy" in report.recommendation
