from datetime import datetime
from decimal import Decimal

from typing import Literal

from pydantic import BaseModel, ConfigDict, Field, field_validator, model_validator


class ProductCreateRequest(BaseModel):
    title: str = Field(min_length=2, max_length=100)
    description: str | None = Field(default=None, max_length=1000)
    price: Decimal = Field(gt=0)
    category_id: int = Field(gt=0)
    trade_location: str = Field(min_length=2, max_length=100)
    image_urls: list[str] = Field(default_factory=list, max_length=6)

    @field_validator('title', 'trade_location')
    @classmethod
    def strip_text(cls, value: str) -> str:
        return value.strip()

    @model_validator(mode='after')
    def validate_required_text(self) -> 'ProductCreateRequest':
        if len(self.title) < 2:
            raise ValueError('商品标题至少需要 2 个字符')
        if len(self.trade_location) < 2:
            raise ValueError('交易地点至少需要 2 个字符')
        return self

    @field_validator('image_urls')
    @classmethod
    def clean_image_urls(cls, value: list[str]) -> list[str]:
        return [item.strip() for item in value if item.strip()]


class ProductUpdateRequest(ProductCreateRequest):
    pass


class ProductQueryParams(BaseModel):
    keyword: str | None = Field(default=None, max_length=100)
    category_id: int | None = Field(default=None, gt=0)
    min_price: Decimal | None = Field(default=None, ge=0)
    max_price: Decimal | None = Field(default=None, ge=0)
    sort_by: Literal['publish_time', 'price'] = 'publish_time'
    sort_order: Literal['asc', 'desc'] = 'desc'
    include_offline: bool = False

    @field_validator('keyword')
    @classmethod
    def strip_keyword(cls, value: str | None) -> str | None:
        if value is None:
            return None
        stripped = value.strip()
        return stripped or None


class ProductResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

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


class CategoryCreateRequest(BaseModel):
    category_name: str = Field(min_length=2, max_length=50)
    description: str | None = Field(default=None, max_length=255)
    sort_order: int = Field(default=0, ge=0)

    @field_validator('category_name')
    @classmethod
    def strip_category_name(cls, value: str) -> str:
        return value.strip()

    @model_validator(mode='after')
    def validate_required_text(self) -> 'CategoryCreateRequest':
        if len(self.category_name) < 2:
            raise ValueError('分类名称至少需要 2 个字符')
        return self


class CategoryUpdateRequest(CategoryCreateRequest):
    status: Literal['ACTIVE', 'DISABLED'] = 'ACTIVE'


class CategoryResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    category_id: int
    category_name: str
    description: str | None = None
    sort_order: int
    status: str
    create_time: datetime
    update_time: datetime
