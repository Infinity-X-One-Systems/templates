"""Tests for the SEO automation engine."""
from src.engine import SEOEngine


def test_missing_title_issue():
    engine = SEOEngine()
    html = "<html><body><h1>Hello</h1><p>Content here with enough words to pass.</p></body></html>"
    result = engine.analyze_content(html)
    issue_types = [i.category for i in result.issues]
    assert "on-page" in issue_types


def test_full_page_no_critical_issues():
    engine = SEOEngine()
    html = """<html><head>
    <title>SEO Optimized Page Title Goes Here For Best Results</title>
    <meta name="description" content="This is a great meta description that is about 155 characters long to satisfy SEO requirements for search engines." />
    </head><body>
    <h1>Main Heading With Keywords</h1>
    <p>This is a well-written page with substantial content about the topic at hand.
    It covers all the important aspects and provides value to the reader.
    More content here to ensure we have sufficient word count for good SEO performance.</p>
    </body></html>"""
    result = engine.analyze_content(html, "keywords")
    critical_issues = [i for i in result.issues if i.severity == "critical"]
    assert len(critical_issues) == 0


def test_score_range():
    engine = SEOEngine()
    html = "<html><head><title>Valid Title Here For SEO Analysis</title></head><body><h1>H1</h1></body></html>"
    result = engine.analyze_content(html)
    assert 0 <= result.score.overall <= 100
    assert 0 <= result.score.on_page <= 100
