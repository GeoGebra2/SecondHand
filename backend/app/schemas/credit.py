from pydantic import BaseModel


class CreditMetricResponse(BaseModel):
    completed_orders: int
    cancelled_orders: int
    total_orders: int
    completion_rate: float
    cancellation_rate: float
    average_review_score: float | None = None
    review_count: int
    published_products: int
    active_orders: int
    activity_score: float
    popularity_score: float


class CreditAnalysisResponse(BaseModel):
    user_id: int
    user_name: str
    email: str
    role: str
    base_credit_score: int
    computed_score: int
    credit_level: str
    risk_level: str
    is_suspicious: bool
    warning_reasons: list[str]
    metrics: CreditMetricResponse
