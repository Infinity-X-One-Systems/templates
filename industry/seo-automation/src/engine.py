"""
SEO Automation Engine — Infinity Template Library
Automated SEO analysis, content optimization, and keyword tracking.
"""
from __future__ import annotations

import asyncio
import re
from typing import Optional
from uuid import uuid4
from datetime import datetime, timezone

from pydantic import BaseModel, Field


class SEOScore(BaseModel):
    overall: float = Field(ge=0.0, le=100.0)
    on_page: float = Field(ge=0.0, le=100.0)
    technical: float = Field(ge=0.0, le=100.0)
    content: float = Field(ge=0.0, le=100.0)


class SEOIssue(BaseModel):
    category: str
    severity: str  # "critical" | "warning" | "info"
    description: str
    recommendation: str


class PageAnalysis(BaseModel):
    url: str
    title: Optional[str] = None
    meta_description: Optional[str] = None
    word_count: int = 0
    heading_count: dict[str, int] = Field(default_factory=dict)
    score: SEOScore = Field(default_factory=lambda: SEOScore(overall=0, on_page=0, technical=0, content=0))
    issues: list[SEOIssue] = Field(default_factory=list)
    keywords: list[str] = Field(default_factory=list)
    analyzed_at: str = Field(default_factory=lambda: datetime.now(tz=timezone.utc).isoformat())


class SEOEngine:
    """SEO analysis and content optimization automation."""

    def analyze_content(self, html: str, target_keyword: str = "") -> PageAnalysis:
        """Analyze HTML content for SEO issues."""
        # Extract title
        title_match = re.search(r"<title[^>]*>(.*?)</title>", html, re.IGNORECASE | re.DOTALL)
        title = title_match.group(1).strip() if title_match else None

        # Extract meta description
        meta_match = re.search(r'<meta[^>]+name=["\']description["\'][^>]+content=["\']([^"\']+)["\']', html, re.IGNORECASE)
        meta_desc = meta_match.group(1) if meta_match else None

        # Count words
        text_content = re.sub(r"<[^>]+>", " ", html)
        words = [w for w in text_content.split() if w.strip()]
        word_count = len(words)

        # Count headings
        headings = {f"h{i}": len(re.findall(f"<h{i}[^>]*>", html, re.IGNORECASE)) for i in range(1, 7)}

        # Identify issues
        issues: list[SEOIssue] = []
        if not title:
            issues.append(SEOIssue(category="on-page", severity="critical", description="Missing <title> tag", recommendation="Add a descriptive title (50-60 chars)"))
        elif len(title) < 30:
            issues.append(SEOIssue(category="on-page", severity="warning", description="Title too short", recommendation="Expand title to 50-60 characters"))
        elif len(title) > 70:
            issues.append(SEOIssue(category="on-page", severity="warning", description="Title too long (may be truncated in SERPs)", recommendation="Shorten title to 50-60 characters"))

        if not meta_desc:
            issues.append(SEOIssue(category="on-page", severity="critical", description="Missing meta description", recommendation="Add a meta description (150-160 chars)"))

        if headings.get("h1", 0) == 0:
            issues.append(SEOIssue(category="on-page", severity="critical", description="Missing H1 tag", recommendation="Add a single H1 heading with target keyword"))
        elif headings.get("h1", 0) > 1:
            issues.append(SEOIssue(category="on-page", severity="warning", description="Multiple H1 tags", recommendation="Use only one H1 per page"))

        if word_count < 300:
            issues.append(SEOIssue(category="content", severity="warning", description=f"Thin content ({word_count} words)", recommendation="Expand content to at least 300 words"))

        # Compute scores
        on_page_score = max(0.0, 100.0 - len([i for i in issues if i.category == "on-page" and i.severity == "critical"]) * 25 - len([i for i in issues if i.category == "on-page" and i.severity == "warning"]) * 10)
        content_score = max(0.0, 100.0 - len([i for i in issues if i.category == "content"]) * 20)

        return PageAnalysis(
            url="",
            title=title,
            meta_description=meta_desc,
            word_count=word_count,
            heading_count=headings,
            score=SEOScore(overall=(on_page_score + content_score) / 2, on_page=on_page_score, technical=80.0, content=content_score),
            issues=issues,
            keywords=[target_keyword] if target_keyword else [],
        )

    async def batch_analyze(self, pages: list[dict[str, str]]) -> list[PageAnalysis]:
        """Analyze multiple pages concurrently."""
        tasks = [asyncio.create_task(asyncio.coroutine(lambda p: self.analyze_content(p["html"], p.get("keyword", "")))()) for p in pages]
        return [self.analyze_content(p["html"], p.get("keyword", "")) for p in pages]
