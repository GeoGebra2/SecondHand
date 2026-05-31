from functools import lru_cache
from typing import List

from pydantic import Field
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    app_name: str = Field(default='校园二手交易平台 API')
    app_version: str = Field(default='0.1.0')
    cors_origins: List[str] = Field(default_factory=lambda: ['http://localhost:5173'])
    database_url: str = Field(
        default='mysql+pymysql://secondhand_user:secondhand123@127.0.0.1:3307/secondhand'
    )
    jwt_secret_key: str = Field(default='change_me')
    jwt_algorithm: str = Field(default='HS256')
    jwt_expire_minutes: int = Field(default=120)

    model_config = SettingsConfigDict(env_file='.env', extra='ignore')


@lru_cache
def get_settings() -> Settings:
    return Settings()
