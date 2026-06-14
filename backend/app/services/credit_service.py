from collections import defaultdict

from sqlalchemy import func, select
from sqlalchemy.orm import Session

from app.models.order_info import OrderInfo
from app.models.product import Product
from app.models.review import Review
from app.models.user import User
from app.models.user_report import UserReport
from app.schemas.credit import CreditAnalysisResponse, CreditMetricResponse, UserRiskProfileResponse


class CreditAnalysisService:
    def analyze_users(self, db: Session) -> list[CreditAnalysisResponse]:
        users = db.scalars(select(User).order_by(User.user_id.asc())).all()
        if not users:
            return []

        order_stats = self._get_order_stats(db)
        seller_review_stats = self._get_seller_review_stats(db)
        report_stats = self._get_report_stats(db)
        product_stats = self._get_product_stats(db)

        analyses = [
            self._build_user_analysis(
                user=user,
                order_stats=order_stats.get(user.user_id, self._empty_order_stats()),
                seller_review_stats=seller_review_stats.get(user.user_id, self._empty_seller_review_stats()),
                report_count=report_stats.get(user.user_id, 0),
                published_products=product_stats.get(user.user_id, 0),
            )
            for user in users
        ]
        return sorted(analyses, key=lambda item: (item.is_suspicious, item.computed_score), reverse=True)

    def get_user_risk_profile(self, db: Session, user_id: int) -> UserRiskProfileResponse:
        user = db.get(User, user_id)
        if user is None:
            raise ValueError('用户不存在')

        analysis = self._build_user_analysis(
            user=user,
            order_stats=self._get_order_stats(db).get(user.user_id, self._empty_order_stats()),
            seller_review_stats=self._get_seller_review_stats(db).get(user.user_id, self._empty_seller_review_stats()),
            report_count=self._get_report_stats(db).get(user.user_id, 0),
            published_products=self._get_product_stats(db).get(user.user_id, 0),
        )
        return UserRiskProfileResponse(
            user_id=analysis.user_id,
            user_name=analysis.user_name,
            computed_score=analysis.computed_score,
            credit_level=analysis.credit_level,
            risk_level=analysis.risk_level,
            is_suspicious=analysis.is_suspicious,
            warning_reasons=analysis.warning_reasons,
            responsible_cancellation_rate=analysis.metrics.responsible_cancellation_rate,
            report_count=analysis.metrics.report_count,
            average_seller_review_score=analysis.metrics.average_seller_review_score,
        )

    def _get_order_stats(self, db: Session) -> dict[int, dict[str, int]]:
        orders = db.scalars(select(OrderInfo)).all()
        stats: dict[int, dict[str, int]] = defaultdict(self._empty_order_stats)
        for order in orders:
            is_accountable_order = order.order_status in {'IN_PROGRESS', 'COMPLETED'} or (
                order.order_status == 'CANCELLED' and order.cancel_user_id is not None
            )
            if is_accountable_order:
                stats[order.buyer_id]['accountable_order_count'] += 1
                stats[order.seller_id]['accountable_order_count'] += 1
            if order.order_status == 'IN_PROGRESS':
                stats[order.buyer_id]['active_orders'] += 1
                stats[order.seller_id]['active_orders'] += 1
            if order.order_status == 'CANCELLED' and order.cancel_user_id is not None:
                stats[order.cancel_user_id]['responsible_cancelled_orders'] += 1
        return dict(stats)

    def _get_seller_review_stats(self, db: Session) -> dict[int, dict[str, float | int]]:
        rows = db.execute(
            select(
                Review.reviewed_user_id,
                func.count(Review.review_id),
                func.avg(Review.score),
            ).group_by(Review.reviewed_user_id)
        ).all()
        return {
            user_id: {
                'seller_review_count': int(review_count),
                'average_seller_review_score': float(average_score or 0),
            }
            for user_id, review_count, average_score in rows
        }

    def _get_report_stats(self, db: Session) -> dict[int, int]:
        rows = db.execute(
            select(UserReport.reported_user_id, func.count(UserReport.report_id)).group_by(UserReport.reported_user_id)
        ).all()
        return {reported_user_id: int(report_count) for reported_user_id, report_count in rows}

    def _get_product_stats(self, db: Session) -> dict[int, int]:
        rows = db.execute(select(Product.seller_id, func.count(Product.product_id)).group_by(Product.seller_id)).all()
        return {seller_id: int(product_count) for seller_id, product_count in rows}

    def _build_user_analysis(
        self,
        user: User,
        order_stats: dict[str, int],
        seller_review_stats: dict[str, float | int],
        report_count: int,
        published_products: int,
    ) -> CreditAnalysisResponse:
        accountable_order_count = order_stats['accountable_order_count']
        responsible_cancelled_orders = order_stats['responsible_cancelled_orders']
        active_orders = order_stats['active_orders']
        responsible_cancellation_rate = (
            responsible_cancelled_orders / accountable_order_count
            if accountable_order_count
            else 0.0
        )

        seller_review_count = int(seller_review_stats['seller_review_count'])
        average_seller_review_score = (
            float(seller_review_stats['average_seller_review_score'])
            if seller_review_count > 0
            else None
        )

        seller_rating_component = ((average_seller_review_score or 4.0) / 5) * 75
        cancellation_component = max(0.0, 5 - responsible_cancellation_rate * 10)
        report_component = max(0.0, 15 - min(report_count, 5) * 3)
        activity_score = min(3.0, (accountable_order_count + published_products) * 0.5)
        popularity_score = min(2.0, published_products * 0.3 + seller_review_count * 0.2)
        computed_score = round(
            seller_rating_component
            + cancellation_component
            + report_component
            + activity_score
            + popularity_score
        )
        computed_score = max(0, min(100, computed_score))

        warning_reasons = self._build_warning_reasons(
            accountable_order_count=accountable_order_count,
            responsible_cancellation_rate=responsible_cancellation_rate,
            seller_review_count=seller_review_count,
            average_seller_review_score=average_seller_review_score,
            report_count=report_count,
        )
        risk_level = self._risk_level(computed_score, warning_reasons)

        return CreditAnalysisResponse(
            user_id=user.user_id,
            user_name=user.user_name,
            email=user.email,
            role=user.role,
            status=user.status,
            base_credit_score=user.credit_score,
            computed_score=computed_score,
            credit_level=self._credit_level(computed_score),
            risk_level=risk_level,
            is_suspicious=risk_level in {'HIGH', 'MEDIUM'},
            warning_reasons=warning_reasons,
            metrics=CreditMetricResponse(
                accountable_order_count=accountable_order_count,
                responsible_cancelled_orders=responsible_cancelled_orders,
                responsible_cancellation_rate=round(responsible_cancellation_rate, 4),
                active_orders=active_orders,
                average_seller_review_score=(
                    round(average_seller_review_score, 2) if average_seller_review_score is not None else None
                ),
                seller_review_count=seller_review_count,
                report_count=report_count,
                published_products=published_products,
                activity_score=round(activity_score, 2),
                popularity_score=round(popularity_score, 2),
            ),
        )

    def _build_warning_reasons(
        self,
        accountable_order_count: int,
        responsible_cancellation_rate: float,
        seller_review_count: int,
        average_seller_review_score: float | None,
        report_count: int,
    ) -> list[str]:
        reasons = []
        if accountable_order_count >= 3 and responsible_cancellation_rate >= 0.5:
            reasons.append('已接单后主动取消率偏高')
        if seller_review_count >= 2 and average_seller_review_score is not None and average_seller_review_score < 3:
            reasons.append('卖家订单评分偏低')
        if report_count >= 2:
            reasons.append('被举报次数较多')
        return reasons

    def _credit_level(self, score: int) -> str:
        if score >= 90:
            return 'A'
        if score >= 75:
            return 'B'
        if score >= 60:
            return 'C'
        return 'D'

    def _risk_level(self, score: int, warning_reasons: list[str]) -> str:
        if score < 60 or len(warning_reasons) >= 2:
            return 'HIGH'
        if score < 75 or warning_reasons:
            return 'MEDIUM'
        return 'LOW'

    def _empty_order_stats(self) -> dict[str, int]:
        return {
            'accountable_order_count': 0,
            'responsible_cancelled_orders': 0,
            'active_orders': 0,
        }

    def _empty_seller_review_stats(self) -> dict[str, float | int]:
        return {
            'seller_review_count': 0,
            'average_seller_review_score': 0.0,
        }


service = CreditAnalysisService()
