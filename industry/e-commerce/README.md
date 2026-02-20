# E-Commerce Engine

Production-grade Python module for product management, order processing, and revenue analytics.

## Quick Start

```bash
pip install -r requirements.txt
python -m src.engine
```

## Run Tests

```bash
pip install -r requirements.txt -r requirements-dev.txt
pytest
```

## Docker

```bash
docker build -t ecommerce-engine .
docker run --rm ecommerce-engine
```

## Features

- Create and manage products with inventory tracking
- Place multi-item orders with automatic total calculation
- Process payments and record transaction IDs
- Update inventory with negative-stock protection
- Calculate revenue metrics: total revenue, average order value, conversion rate
