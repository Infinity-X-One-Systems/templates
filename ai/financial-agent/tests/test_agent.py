"""Tests for the financial agent."""
import pytest
from src.agent import FinancialAgent, AnalysisTask, RiskLevel


@pytest.mark.asyncio
async def test_analyze_symbols():
    agent = FinancialAgent()
    task = AnalysisTask(symbols=["AAPL", "GOOGL"], timeframe="1D")
    result = await agent.analyze(task)
    assert len(result.signals) > 0
    assert result.risk_assessment in list(RiskLevel)
    assert len(result.recommendations) > 0


@pytest.mark.asyncio
async def test_empty_symbols():
    agent = FinancialAgent()
    task = AnalysisTask(symbols=[])
    result = await agent.analyze(task)
    assert result.risk_assessment == RiskLevel.HIGH
    assert result.confidence == 0.0
