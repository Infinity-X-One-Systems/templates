"""Tests for ECommerceEngine."""
import pytest
from src.engine import ECommerceEngine


@pytest.fixture
def engine():
    return ECommerceEngine()


def test_create_product(engine):
    product = engine.create_product("Mechanical Keyboard", 89.99, 200, "electronics")
    assert product.name == "Mechanical Keyboard"
    assert product.price == 89.99
    assert product.inventory == 200
    assert product.category == "electronics"


def test_place_order(engine):
    p1 = engine.create_product("USB Hub", 19.99, 100, "electronics")
    p2 = engine.create_product("Desk Lamp", 34.99, 50, "home")
    order = engine.place_order(
        "CUST001",
        [{"product_id": p1.id, "quantity": 2}, {"product_id": p2.id, "quantity": 1}],
    )
    assert order.customer_id == "CUST001"
    assert order.total == round(19.99 * 2 + 34.99, 2)
    assert len(order.items) == 2


def test_process_payment(engine):
    p = engine.create_product("Notebook", 9.99, 500, "stationery")
    order = engine.place_order("CUST002", [{"product_id": p.id, "quantity": 3}])
    result = engine.process_payment(order.id, "credit_card")
    assert result.success is True
    assert result.transaction_id != ""
    assert engine._orders[order.id].status == "paid"


def test_update_inventory(engine):
    product = engine.create_product("Monitor", 299.99, 10, "electronics")
    updated = engine.update_inventory(product.id, -3)
    assert updated.inventory == 7
    with pytest.raises(ValueError):
        engine.update_inventory(product.id, -100)
