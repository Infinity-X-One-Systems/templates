"""Tests for the financial trading simulator."""
import pytest
from src.simulator import TradingSimulator, OrderSide, OrderStatus


@pytest.mark.asyncio
async def test_buy_order():
    sim = TradingSimulator(initial_cash=10_000.0)
    sim.set_price("AAPL", 150.0)
    order = await sim.place_order("AAPL", OrderSide.BUY, 10, price=150.0)
    assert order.status == OrderStatus.FILLED
    assert "AAPL" in sim.portfolio.positions
    assert sim.portfolio.cash == 8_500.0


@pytest.mark.asyncio
async def test_sell_order():
    sim = TradingSimulator(initial_cash=10_000.0)
    sim.set_price("AAPL", 150.0)
    await sim.place_order("AAPL", OrderSide.BUY, 10, price=150.0)
    sim.set_price("AAPL", 160.0)
    order = await sim.place_order("AAPL", OrderSide.SELL, 10, price=160.0)
    assert order.status == OrderStatus.FILLED
    assert "AAPL" not in sim.portfolio.positions
    assert sim.portfolio.cash == 10_100.0  # 10000 - 1500 (buy) + 1600 (sell)


@pytest.mark.asyncio
async def test_insufficient_funds():
    sim = TradingSimulator(initial_cash=100.0)
    sim.set_price("AAPL", 150.0)
    order = await sim.place_order("AAPL", OrderSide.BUY, 10, price=150.0)
    assert order.status == OrderStatus.REJECTED


@pytest.mark.asyncio
async def test_portfolio_value():
    sim = TradingSimulator(initial_cash=10_000.0)
    sim.set_price("AAPL", 100.0)
    await sim.place_order("AAPL", OrderSide.BUY, 50, price=100.0)
    sim.set_price("AAPL", 110.0)
    assert sim.portfolio.total_value == 10_500.0  # 5000 cash + 5500 position
