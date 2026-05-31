from datetime import datetime
from decimal import Decimal

from pydantic import BaseModel, Field


class OrderCreateRequest(BaseModel):
    product_id: int
    buyer_note: str | None = Field(default=None, max_length=255)


class OrderActionRequest(BaseModel):
    cancel_reason: str | None = Field(default=None, max_length=255)


class OrderResponse(BaseModel):
    order_id: int
    product_id: int
    product_title: str
    buyer_id: int
    buyer_name: str
    seller_id: int
    seller_name: str
    order_amount: Decimal
    order_status: str
    trade_method: str
    trade_location: str
    buyer_note: str | None = None
    cancel_reason: str | None = None
    create_time: datetime
    update_time: datetime
    finish_time: datetime | None = None
    can_review: bool = False


class OrderStatusResponse(BaseModel):
    order_id: int
    order_status: str
    product_status: str
