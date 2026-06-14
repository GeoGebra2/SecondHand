from pydantic import BaseModel


class CreditMetricResponse(BaseModel):
    accountable_order_count: int
    responsible_cancelled_orders: int
    responsible_cancellation_rate: float
    active_orders: int
    average_seller_review_score: float | None = None
    seller_review_count: int
    report_count: int
    published_products: int
    activity_score: float
    popularity_score: float


class CreditAnalysisResponse(BaseModel):
    user_id: int
    user_name: str
    email: str
    role: str
    status: str
    base_credit_score: int
    computed_score: int
    credit_level: str
    risk_level: str
    is_suspicious: bool
    warning_reasons: list[str]
    metrics: CreditMetricResponse


class UserRiskProfileResponse(BaseModel):
    user_id: int
    user_name: str
    computed_score: int
    credit_level: str
    risk_level: str
    is_suspicious: bool
    warning_reasons: list[str]
    responsible_cancellation_rate: float
    report_count: int
    average_seller_review_score: float | None = None
