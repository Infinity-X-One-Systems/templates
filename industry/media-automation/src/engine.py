from __future__ import annotations
import uuid
from datetime import datetime
from typing import List, Optional
from pydantic import BaseModel, Field


class ContentBrief(BaseModel):
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    title: str
    type: str
    target_audience: str
    keywords: List[str]
    due_date: datetime
    cost: float = 500.0
    created_at: datetime = Field(default_factory=datetime.utcnow)


class ScheduledPost(BaseModel):
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    content_id: str
    platform: str
    publish_at: datetime
    status: str = "scheduled"


class PerformanceMetrics(BaseModel):
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    content_id: str
    platform: str
    views: int
    engagements: int
    shares: int
    engagement_rate: float
    recorded_at: datetime = Field(default_factory=datetime.utcnow)


class MediaAutomationEngine:
    def __init__(self) -> None:
        self._briefs: dict[str, ContentBrief] = {}
        self._posts: list[ScheduledPost] = []
        self._metrics: list[PerformanceMetrics] = []

    def create_content_brief(
        self,
        title: str,
        type: str,
        target_audience: str,
        keywords: list[str],
        due_date: datetime,
        cost: float = 500.0,
    ) -> ContentBrief:
        brief = ContentBrief(
            title=title,
            type=type,
            target_audience=target_audience,
            keywords=keywords,
            due_date=due_date,
            cost=cost,
        )
        self._briefs[brief.id] = brief
        return brief

    def schedule_publication(
        self,
        content_id: str,
        platform: str,
        publish_at: datetime,
    ) -> ScheduledPost:
        post = ScheduledPost(
            content_id=content_id,
            platform=platform,
            publish_at=publish_at,
        )
        self._posts.append(post)
        return post

    def track_performance(
        self,
        content_id: str,
        platform: str,
        views: int,
        engagements: int,
        shares: int,
    ) -> PerformanceMetrics:
        engagement_rate = (engagements / views) if views > 0 else 0.0
        m = PerformanceMetrics(
            content_id=content_id,
            platform=platform,
            views=views,
            engagements=engagements,
            shares=shares,
            engagement_rate=engagement_rate,
        )
        self._metrics.append(m)
        return m

    def calculate_content_roi(self, content_id: str) -> float:
        brief = self._briefs.get(content_id)
        if brief is None:
            return 0.0
        metrics = [m for m in self._metrics if m.content_id == content_id]
        if not metrics:
            return 0.0
        avg_engagement_rate = sum(m.engagement_rate for m in metrics) / len(metrics)
        total_views = sum(m.views for m in metrics)
        cost = brief.cost
        if cost == 0:
            return 0.0
        return avg_engagement_rate * total_views / cost

    def generate_content_calendar(
        self, briefs: list[ContentBrief], month_str: str
    ) -> list[ScheduledPost]:
        year, month = int(month_str.split("-")[0]), int(month_str.split("-")[1])
        brief_ids = {b.id for b in briefs}
        posts = [
            p for p in self._posts
            if p.content_id in brief_ids
            and p.publish_at.year == year
            and p.publish_at.month == month
        ]
        return sorted(posts, key=lambda p: p.publish_at)
