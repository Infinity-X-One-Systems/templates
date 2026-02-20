from src.engine import KnowledgeMonetizationEngine


def test_create_asset():
    engine = KnowledgeMonetizationEngine()
    asset = engine.create_asset("Python Mastery", "course", 99.0, "creator-1", "Learn Python")
    assert asset.title == "Python Mastery"
    assert asset.type == "course"
    assert asset.price == 99.0


def test_record_sale():
    engine = KnowledgeMonetizationEngine()
    asset = engine.create_asset("SaaS Blueprint", "saas", 299.0, "creator-2", "Build SaaS")
    sale = engine.record_sale(asset.id, "buyer-1", 299.0)
    assert sale.asset_id == asset.id
    assert sale.price_paid == 299.0


def test_calculate_royalties():
    engine = KnowledgeMonetizationEngine()
    asset = engine.create_asset("eBook Pro", "ebook", 29.0, "creator-3", "Pro tips")
    sale1 = engine.record_sale(asset.id, "buyer-1", 29.0)
    sale2 = engine.record_sale(asset.id, "buyer-2", 29.0)
    report = engine.calculate_royalties("creator-3", [sale1, sale2])
    assert report.total == 58.0
    assert report.by_asset[asset.id] == 58.0


def test_generate_creator_dashboard():
    engine = KnowledgeMonetizationEngine()
    asset = engine.create_asset("Template Pack", "template", 49.0, "creator-4", "Templates")
    engine.record_sale(asset.id, "buyer-1", 49.0)
    engine.record_sale(asset.id, "buyer-2", 49.0)
    dashboard = engine.generate_creator_dashboard("creator-4")
    assert dashboard.revenue == 98.0
    assert dashboard.sales == 2
    assert asset.id in dashboard.top_assets
