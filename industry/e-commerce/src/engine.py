"""E-Commerce Engine – products, orders, payments, inventory, and revenue analytics."""
from __future__ import annotations

import uuid
from typing import Dict, List

from pydantic import BaseModel, Field


class Product(BaseModel):
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    name: str
    price: float
    inventory: int
    category: str


class OrderItem(BaseModel):
    product_id: str
    quantity: int
    unit_price: float


class Order(BaseModel):
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    customer_id: str
    items: List[OrderItem]
    total: float
    status: str = "pending"


class PaymentResult(BaseModel):
    order_id: str
    success: bool
    transaction_id: str
    message: str = ""


class RevenueMetrics(BaseModel):
    total_revenue: float
    avg_order_value: float
    conversion_rate: float


class ECommerceEngine:
    """Manages products, orders, payments, inventory, and revenue metrics."""

    def __init__(self) -> None:
        self._products: Dict[str, Product] = {}
        self._orders: Dict[str, Order] = {}

    def create_product(
        self, name: str, price: float, inventory: int, category: str
    ) -> Product:
        product = Product(name=name, price=price, inventory=inventory, category=category)
        self._products[product.id] = product
        return product

    def place_order(self, customer_id: str, items: List[dict]) -> Order:
        order_items: List[OrderItem] = []
        total = 0.0
        for item in items:
            product = self._get_product(item["product_id"])
            qty = item["quantity"]
            order_items.append(
                OrderItem(product_id=product.id, quantity=qty, unit_price=product.price)
            )
            total += product.price * qty
        order = Order(customer_id=customer_id, items=order_items, total=round(total, 2))
        self._orders[order.id] = order
        return order

    def process_payment(self, order_id: str, payment_method: str) -> PaymentResult:
        if order_id not in self._orders:
            return PaymentResult(
                order_id=order_id, success=False, transaction_id="", message="Order not found"
            )
        order = self._orders[order_id]
        transaction_id = str(uuid.uuid4())
        order.status = "paid"
        return PaymentResult(order_id=order_id, success=True, transaction_id=transaction_id)

    def update_inventory(self, product_id: str, quantity_delta: int) -> Product:
        product = self._get_product(product_id)
        new_qty = product.inventory + quantity_delta
        if new_qty < 0:
            raise ValueError(
                f"Inventory cannot go negative: current={product.inventory}, delta={quantity_delta}"
            )
        product.inventory = new_qty
        return product

    def calculate_revenue_metrics(self, orders: List[Order]) -> RevenueMetrics:
        paid_orders = [o for o in orders if o.status == "paid"]
        total_revenue = round(sum(o.total for o in paid_orders), 2)
        avg_order_value = round(total_revenue / len(paid_orders), 2) if paid_orders else 0.0
        conversion_rate = round(len(paid_orders) / len(orders), 4) if orders else 0.0
        return RevenueMetrics(
            total_revenue=total_revenue,
            avg_order_value=avg_order_value,
            conversion_rate=conversion_rate,
        )

    def _get_product(self, product_id: str) -> Product:
        if product_id not in self._products:
            raise KeyError(f"Product {product_id} not found")
        return self._products[product_id]


if __name__ == "__main__":
    engine = ECommerceEngine()
    product = engine.create_product("Wireless Mouse", 29.99, 150, "electronics")
    print(f"Product created: {product.name} (id={product.id})")
