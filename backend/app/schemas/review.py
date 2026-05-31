from datetime import datetime

from pydantic import BaseModel, ConfigDict, Field


class ReviewCreateRequest(BaseModel):
    order_id: int
    score: int = Field(ge=1, le=5)
    content: str = Field(min_length=2, max_length=255)


class ReviewResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    review_id: int
    order_id: int
    reviewer_id: int
    reviewer_name: str
    reviewed_user_id: int
    reviewed_user_name: str
    score: int
    content: str
    create_time: datetime
