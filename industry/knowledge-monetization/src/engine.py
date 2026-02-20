from __future__ import annotations
import uuid
from datetime import datetime, timezone
from typing import Dict, List, Optional
from pydantic import BaseModel, Field


ASSET_TYPES = {"course", "ebook", "template", "consulting", "saas"}


class KnowledgeAsset(BaseModel):
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    title: str
    type: str
    price: float
    creator_id: str
    description: str
    created_at: datetime = Field(default_factory=datetime.utcnow)


class Sale(BaseModel):
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    asset_id: str
    buyer_id: str
    price_paid: float
    sold_at: datetime = Field(default_factory=datetime.utcnow)


class RoyaltyReport(BaseModel):
    creator_id: str
    total: float
    by_asset: Dict[str, float]


class Subscription(BaseModel):
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    creator_id: str
    subscriber_id: str
    tier: str
    started_at: datetime = Field(default_factory=datetime.utcnow)


class CreatorDashboard(BaseModel):
    creator_id: str
    revenue: float
    sales: int
    top_assets: List[str]


class KnowledgeMonetizationEngine:
    def __init__(self) -> None:
        self._assets: dict[str, KnowledgeAsset] = {}
        self._sales: list[Sale] = []
        self._subscriptions: list[Subscription] = []

    def create_asset(
        self,
        title: str,
        type: str,
        price: float,
        creator_id: str,
        description: str,
    ) -> KnowledgeAsset:
        if type not in ASSET_TYPES:
            raise ValueError(f"Invalid asset type: {type}. Must be one of {ASSET_TYPES}")
        asset = KnowledgeAsset(
            title=title,
            type=type,
            price=price,
            creator_id=creator_id,
            description=description,
        )
        self._assets[asset.id] = asset
        return asset

    def record_sale(
        self,
        asset_id: str,
        buyer_id: str,
        price_paid: float,
    ) -> Sale:
        if asset_id not in self._assets:
            raise ValueError(f"Asset {asset_id} not found")
        sale = Sale(asset_id=asset_id, buyer_id=buyer_id, price_paid=price_paid)
        self._sales.append(sale)
        return sale

    def calculate_royalties(
        self,
        creator_id: str,
        period_sales: list[Sale],
    ) -> RoyaltyReport:
        creator_assets = {a.id for a in self._assets.values() if a.creator_id == creator_id}
        relevant = [s for s in period_sales if s.asset_id in creator_assets]
        by_asset: dict[str, float] = {}
        for sale in relevant:
            by_asset[sale.asset_id] = by_asset.get(sale.asset_id, 0.0) + sale.price_paid
        total = sum(by_asset.values())
        return RoyaltyReport(creator_id=creator_id, total=total, by_asset=by_asset)

    def track_subscriber(
        self,
        creator_id: str,
        subscriber_id: str,
        tier: str,
    ) -> Subscription:
        sub = Subscription(creator_id=creator_id, subscriber_id=subscriber_id, tier=tier)
        self._subscriptions.append(sub)
        return sub

    def generate_creator_dashboard(self, creator_id: str) -> CreatorDashboard:
        creator_assets = {a.id: a for a in self._assets.values() if a.creator_id == creator_id}
        sales = [s for s in self._sales if s.asset_id in creator_assets]
        revenue = sum(s.price_paid for s in sales)
        asset_revenue: dict[str, float] = {}
        for sale in sales:
            asset_revenue[sale.asset_id] = asset_revenue.get(sale.asset_id, 0.0) + sale.price_paid
        top_assets = sorted(asset_revenue, key=lambda k: asset_revenue[k], reverse=True)[:5]
        return CreatorDashboard(
            creator_id=creator_id,
            revenue=revenue,
            sales=len(sales),
            top_assets=top_assets,
        )
