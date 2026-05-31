from datetime import datetime
from decimal import Decimal

from pydantic import BaseModel, ConfigDict, Field, field_validator


class ProductCreateRequest(BaseModel):
    title: str = Field(min_length=2, max_length=100)
    description: str | None = Field(default=None, max_length=1000)
    price: Decimal = Field(gt=0)
    category_name: str = Field(min_length=2, max_length=50)
    trade_location: str = Field(min_length=2, max_length=100)

    @field_validator('title', 'category_name', 'trade_location')
    @classmethod
    def strip_text(cls, value: str) -> str:
        return value.strip()


class ProductResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    product_id: int
    seller_id: int
    seller_name: str
    title: str
    description: str | None = None
    price: Decimal
    category_name: str
    trade_location: str
    status: str
    publish_time: datetime
    update_time: datetime
