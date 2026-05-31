from datetime import datetime

from pydantic import BaseModel, ConfigDict, EmailStr, Field


class UserProfileResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    user_id: int
    student_no: str
    user_name: str
    gender: str | None = None
    phone: str | None = None
    email: EmailStr
    role: str
    credit_score: int
    status: str
    verify_status: str
    avatar_url: str | None = None
    bio: str | None = None
    create_time: datetime
    update_time: datetime
    last_login_time: datetime | None = None


class UserProfileUpdateRequest(BaseModel):
    user_name: str | None = Field(default=None, min_length=2, max_length=50)
    phone: str | None = Field(default=None, min_length=6, max_length=20)
    email: EmailStr | None = None
    gender: str | None = Field(default=None, max_length=10)
    avatar_url: str | None = Field(default=None, max_length=255)
    bio: str | None = Field(default=None, max_length=255)
