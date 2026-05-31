from typing import Any

from pydantic import BaseModel


class ApiResponse(BaseModel):
    message: str
    data: Any = None


class OverviewCard(BaseModel):
    label: str
    value: str
    description: str
