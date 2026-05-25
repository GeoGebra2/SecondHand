from functools import lru_cache
from typing import List

from pydantic import Field
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    app_name: str = Field(default='校园二手交易平台 API')
    app_version: str = Field(default='0.1.0')
    cors_origins: List[str] = Field(default_factory=lambda: ['http://localhost:5173'])

    model_config = SettingsConfigDict(env_file='.env', extra='ignore')


@lru_cache
def get_settings() -> Settings:
    return Settings()
