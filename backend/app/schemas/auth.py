from pydantic import BaseModel, EmailStr, Field, field_validator

from app.schemas.user import UserProfileResponse


class RegisterRequest(BaseModel):
    student_no: str = Field(min_length=6, max_length=20)
    user_name: str = Field(min_length=2, max_length=50)
    password: str = Field(min_length=8, max_length=64)
    email: EmailStr
    phone: str = Field(min_length=6, max_length=20)
    gender: str | None = Field(default=None, max_length=10)

    @field_validator('student_no', 'user_name', 'phone')
    @classmethod
    def strip_text(cls, value: str) -> str:
        return value.strip()


class LoginRequest(BaseModel):
    account: str = Field(min_length=3, max_length=100)
    password: str = Field(min_length=8, max_length=64)

    @field_validator('account')
    @classmethod
    def strip_account(cls, value: str) -> str:
        return value.strip()


class TokenResponse(BaseModel):
    access_token: str
    token_type: str = 'bearer'
    expires_in: int
    user: UserProfileResponse
