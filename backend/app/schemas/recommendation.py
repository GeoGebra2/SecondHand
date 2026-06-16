from datetime import datetime
from decimal import Decimal

from pydantic import BaseModel, Field


class RecommendationItem(BaseModel):
    product_id: int
    seller_id: int
    seller_name: str
    title: str
    description: str | None = None
    price: Decimal
    category_id: int
    category_name: str
    trade_location: str
    status: str
    image_urls: list[str] = Field(default_factory=list)
    publish_time: datetime
    update_time: datetime
    ai_score: float
    ai_reason: str
    ai_tags: list[str] = Field(default_factory=list)


class RecommendationResponse(BaseModel):
    algorithm: str
    profile_summary: str
    items: list[RecommendationItem]


class BrowseRecordRequest(BaseModel):
    product_ids: list[int] = Field(min_length=1, max_length=12)
