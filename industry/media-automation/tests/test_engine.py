from datetime import datetime
from src.engine import MediaAutomationEngine


def test_create_content_brief():
    engine = MediaAutomationEngine()
    brief = engine.create_content_brief(
        "How to Scale", "article", "developers", ["python", "scale"], datetime(2024, 6, 30)
    )
    assert brief.title == "How to Scale"
    assert "python" in brief.keywords


def test_schedule_publication():
    engine = MediaAutomationEngine()
    brief = engine.create_content_brief("Post A", "video", "all", ["ai"], datetime(2024, 7, 1))
    post = engine.schedule_publication(brief.id, "YouTube", datetime(2024, 7, 15, 10, 0))
    assert post.platform == "YouTube"
    assert post.content_id == brief.id


def test_track_performance():
    engine = MediaAutomationEngine()
    m = engine.track_performance("content-1", "Twitter", 1000, 50, 20)
    assert m.views == 1000
    assert abs(m.engagement_rate - 0.05) < 0.001


def test_calculate_content_roi():
    engine = MediaAutomationEngine()
    brief = engine.create_content_brief("ROI Test", "blog", "marketers", ["roi"], datetime(2024, 8, 1), cost=100.0)
    engine.track_performance(brief.id, "LinkedIn", 2000, 100, 50)
    roi = engine.calculate_content_roi(brief.id)
    assert roi > 0
