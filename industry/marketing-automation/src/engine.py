"""Marketing Automation Engine - core engine."""

from __future__ import annotations

import uuid
from datetime import datetime, timezone
from typing import Optional

from pydantic import BaseModel, Field


class Campaign(BaseModel):
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    name: str
    channel: str
    budget: float
    target_audience: str
    start_date: str
    end_date: str
    impressions: int = 0
    conversions: int = 0
    revenue: float = 0.0
    status: str = "active"
    created_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))


class ROIMetrics(BaseModel):
    campaign_id: str
    cpa: float
    roas: float
    roi_pct: float


class CampaignReport(BaseModel):
    campaign_id: str
    name: str
    channel: str
    budget: float
    impressions: int
    conversions: int
    revenue: float
    cpa: float
    roas: float
    roi_pct: float
    click_through_rate: float
    generated_at: datetime


class MarketingAutomationEngine:
    def __init__(self) -> None:
        self._campaigns: dict[str, Campaign] = {}

    def create_campaign(
        self,
        name: str,
        channel: str,
        budget: float,
        target_audience: str,
        start_date: str,
        end_date: str,
    ) -> Campaign:
        campaign = Campaign(
            name=name,
            channel=channel,
            budget=budget,
            target_audience=target_audience,
            start_date=start_date,
            end_date=end_date,
        )
        self._campaigns[campaign.id] = campaign
        return campaign

    def record_impression(self, campaign_id: str) -> Campaign:
        campaign = self._campaigns[campaign_id]
        campaign.impressions += 1
        return campaign

    def record_conversion(self, campaign_id: str, value: float) -> Campaign:
        campaign = self._campaigns[campaign_id]
        campaign.conversions += 1
        campaign.revenue += value
        return campaign

    def calculate_roi(self, campaign_id: str) -> ROIMetrics:
        c = self._campaigns[campaign_id]
        cpa = (c.budget / c.conversions) if c.conversions > 0 else 0.0
        roas = (c.revenue / c.budget) if c.budget > 0 else 0.0
        roi_pct = ((c.revenue - c.budget) / c.budget * 100.0) if c.budget > 0 else 0.0
        return ROIMetrics(
            campaign_id=campaign_id,
            cpa=round(cpa, 2),
            roas=round(roas, 4),
            roi_pct=round(roi_pct, 2),
        )

    def generate_report(self, campaign_id: str) -> CampaignReport:
        c = self._campaigns[campaign_id]
        roi = self.calculate_roi(campaign_id)
        ctr = (c.conversions / c.impressions * 100.0) if c.impressions > 0 else 0.0
        return CampaignReport(
            campaign_id=campaign_id,
            name=c.name,
            channel=c.channel,
            budget=c.budget,
            impressions=c.impressions,
            conversions=c.conversions,
            revenue=c.revenue,
            cpa=roi.cpa,
            roas=roi.roas,
            roi_pct=roi.roi_pct,
            click_through_rate=round(ctr, 4),
            generated_at=datetime.now(timezone.utc),
        )
