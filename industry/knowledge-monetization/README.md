# Knowledge Monetization Engine

A production-grade Python module for creators to monetize knowledge assets including courses, ebooks, templates, consulting, and SaaS products.

## Features
- Create and manage knowledge assets (course, ebook, template, consulting, saas)
- Record sales and track revenue
- Calculate royalties per creator and asset
- Manage subscriber tiers
- Generate creator dashboards with top-performing assets

## Usage
```python
from src.engine import KnowledgeMonetizationEngine

engine = KnowledgeMonetizationEngine()
asset = engine.create_asset("Python Mastery", "course", 99.0, "creator-1", "Learn Python deeply")
sale = engine.record_sale(asset.id, "buyer-1", 99.0)
dashboard = engine.generate_creator_dashboard("creator-1")
```
