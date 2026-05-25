from pydantic import BaseModel


class ApiResponse(BaseModel):
    message: str
    data: dict | list | None = None


class OverviewCard(BaseModel):
    label: str
    value: str
    description: str
