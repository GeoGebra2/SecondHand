from datetime import datetime

from pydantic import BaseModel, ConfigDict, Field


class FavoriteCreateRequest(BaseModel):
    product_id: int = Field(gt=0)


class FavoriteResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    favorite_id: int
    product_id: int
    product_title: str
    category_name: str
    create_time: datetime


class NotificationCreateRequest(BaseModel):
    receiver_id: int = Field(gt=0)
    content: str = Field(min_length=2, max_length=255)


class NotificationResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    notification_id: int
    receiver_id: int
    content: str
    create_time: datetime


class CategoryHeatmapItem(BaseModel):
    category_id: int
    category_name: str
    sales_count: int
    total_revenue: int


class ActiveUserItem(BaseModel):
    user_name: str
    action_count: int


class TradeTrendItem(BaseModel):
    date: str
    amount: int


class DashboardStatsResponse(BaseModel):
    pending_product_count: int
    category_count: int
    recommendation_heat: str
    categories: list[CategoryHeatmapItem]
    users: list[ActiveUserItem]
    trends: list[TradeTrendItem]
