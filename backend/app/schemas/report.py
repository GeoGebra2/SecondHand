from datetime import datetime

from pydantic import BaseModel, ConfigDict, Field, field_validator


class UserReportCreateRequest(BaseModel):
    reported_user_id: int
    reason: str = Field(min_length=2, max_length=100)
    description: str | None = Field(default=None, max_length=1000)

    @field_validator('reason', 'description', mode='before')
    @classmethod
    def strip_text(cls, value: str | None) -> str | None:
        if value is None:
            return None
        stripped = value.strip()
        return stripped or None


class UserReportResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    report_id: int
    reporter_id: int
    reporter_name: str
    reported_user_id: int
    reported_user_name: str
    reason: str
    description: str | None = None
    status: str
    create_time: datetime
    update_time: datetime
