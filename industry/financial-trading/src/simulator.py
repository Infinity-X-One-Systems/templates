"""
Financial Trading Simulator — Infinity Template Library
Paper trading simulator with portfolio tracking and strategy backtesting.
"""
from __future__ import annotations

import asyncio
from datetime import datetime, timezone
from enum import Enum
from typing import Optional
from uuid import uuid4

from pydantic import BaseModel, Field


class OrderSide(str, Enum):
    BUY = "buy"
    SELL = "sell"


class OrderStatus(str, Enum):
    PENDING = "pending"
    FILLED = "filled"
    CANCELLED = "cancelled"
    REJECTED = "rejected"


class Order(BaseModel):
    order_id: str = Field(default_factory=lambda: str(uuid4()))
    symbol: str
    side: OrderSide
    quantity: float
    price: Optional[float] = None  # None = market order
    status: OrderStatus = OrderStatus.PENDING
    filled_price: Optional[float] = None
    created_at: str = Field(default_factory=lambda: datetime.now(tz=timezone.utc).isoformat())
    filled_at: Optional[str] = None


class Position(BaseModel):
    symbol: str
    quantity: float
    avg_price: float
    current_price: float = 0.0

    @property
    def unrealized_pnl(self) -> float:
        return (self.current_price - self.avg_price) * self.quantity

    @property
    def market_value(self) -> float:
        return self.current_price * self.quantity


class Portfolio(BaseModel):
    portfolio_id: str = Field(default_factory=lambda: str(uuid4()))
    cash: float = 100_000.0  # Default paper trading balance
    positions: dict[str, Position] = Field(default_factory=dict)
    orders: list[Order] = Field(default_factory=list)
    created_at: str = Field(default_factory=lambda: datetime.now(tz=timezone.utc).isoformat())

    @property
    def total_value(self) -> float:
        return self.cash + sum(p.market_value for p in self.positions.values())

    @property
    def total_unrealized_pnl(self) -> float:
        return sum(p.unrealized_pnl for p in self.positions.values())


class TradingSimulator:
    """
    Paper trading simulator supporting market and limit orders.
    DISCLAIMER: For educational/simulation purposes only. Not financial advice.
    """

    def __init__(self, initial_cash: float = 100_000.0) -> None:
        self.portfolio = Portfolio(cash=initial_cash)
        self._market_prices: dict[str, float] = {}

    def set_price(self, symbol: str, price: float) -> None:
        """Update the simulated market price for a symbol."""
        self._market_prices[symbol] = price
        if symbol in self.portfolio.positions:
            self.portfolio.positions[symbol].current_price = price

    async def place_order(self, symbol: str, side: OrderSide, quantity: float, price: Optional[float] = None) -> Order:
        """Place a simulated order."""
        await asyncio.sleep(0)
        order = Order(symbol=symbol, side=side, quantity=quantity, price=price)
        fill_price = price or self._market_prices.get(symbol)

        if fill_price is None:
            order.status = OrderStatus.REJECTED
            self.portfolio.orders.append(order)
            return order

        cost = fill_price * quantity
        if side == OrderSide.BUY:
            if self.portfolio.cash < cost:
                order.status = OrderStatus.REJECTED
                self.portfolio.orders.append(order)
                return order
            self.portfolio.cash -= cost
            if symbol in self.portfolio.positions:
                pos = self.portfolio.positions[symbol]
                total_qty = pos.quantity + quantity
                pos.avg_price = (pos.avg_price * pos.quantity + fill_price * quantity) / total_qty
                pos.quantity = total_qty
                pos.current_price = fill_price
            else:
                self.portfolio.positions[symbol] = Position(symbol=symbol, quantity=quantity, avg_price=fill_price, current_price=fill_price)
        elif side == OrderSide.SELL:
            pos = self.portfolio.positions.get(symbol)
            if pos is None or pos.quantity < quantity:
                order.status = OrderStatus.REJECTED
                self.portfolio.orders.append(order)
                return order
            self.portfolio.cash += fill_price * quantity
            pos.quantity -= quantity
            if pos.quantity == 0:
                del self.portfolio.positions[symbol]

        order.status = OrderStatus.FILLED
        order.filled_price = fill_price
        order.filled_at = datetime.now(tz=timezone.utc).isoformat()
        self.portfolio.orders.append(order)
        return order
