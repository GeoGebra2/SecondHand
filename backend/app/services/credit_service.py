from collections import defaultdict

from sqlalchemy import func, select
from sqlalchemy.orm import Session

from app.models.order_info import OrderInfo
from app.models.product import Product
from app.models.review import Review
from app.models.user import User
from app.schemas.credit import CreditAnalysisResponse, CreditMetricResponse


class CreditAnalysisService:
    def analyze_users(self, db: Session) -> list[CreditAnalysisResponse]:
        users = db.scalars(select(User).order_by(User.user_id.asc())).all()
        if not users:
            return []

        order_stats = self._get_order_stats(db)
        review_stats = self._get_review_stats(db)
        product_stats = self._get_product_stats(db)

        analyses = [
            self._build_user_analysis(
                user=user,
                order_stats=order_stats.get(user.user_id, self._empty_order_stats()),
                review_stats=review_stats.get(user.user_id, self._empty_review_stats()),
                published_products=product_stats.get(user.user_id, 0),
            )
            for user in users
        ]
        return sorted(analyses, key=lambda item: (item.is_suspicious, item.computed_score), reverse=True)

    def _get_order_stats(self, db: Session) -> dict[int, dict[str, int]]:
        orders = db.scalars(select(OrderInfo)).all()
        stats: dict[int, dict[str, int]] = defaultdict(self._empty_order_stats)
        for order in orders:
            # Credit analysis uses transaction participation, so both buyer and seller receive one activity record.
            for user_id in {order.buyer_id, order.seller_id}:
                stats[user_id]['total_orders'] += 1
                if order.order_status == 'COMPLETED':
                    stats[user_id]['completed_orders'] += 1
                elif order.order_status == 'CANCELLED':
                    stats[user_id]['cancelled_orders'] += 1
                elif order.order_status in {'PENDING', 'IN_PROGRESS'}:
                    stats[user_id]['active_orders'] += 1
        return dict(stats)

    def _get_review_stats(self, db: Session) -> dict[int, dict[str, float | int]]:
        rows = db.execute(
            select(
                Review.reviewed_user_id,
                func.count(Review.review_id),
                func.avg(Review.score),
            ).group_by(Review.reviewed_user_id)
        ).all()
        return {
            user_id: {
                'review_count': int(review_count),
                'average_review_score': float(average_score or 0),
            }
            for user_id, review_count, average_score in rows
        }

    def _get_product_stats(self, db: Session) -> dict[int, int]:
        rows = db.execute(select(Product.seller_id, func.count(Product.product_id)).group_by(Product.seller_id)).all()
        return {seller_id: int(product_count) for seller_id, product_count in rows}

    def _build_user_analysis(
        self,
        user: User,
        order_stats: dict[str, int],
        review_stats: dict[str, float | int],
        published_products: int,
    ) -> CreditAnalysisResponse:
        total_orders = order_stats['total_orders']
        completed_orders = order_stats['completed_orders']
        cancelled_orders = order_stats['cancelled_orders']
        active_orders = order_stats['active_orders']
        completion_rate = completed_orders / total_orders if total_orders else 1.0
        cancellation_rate = cancelled_orders / total_orders if total_orders else 0.0
        review_count = int(review_stats['review_count'])
        average_review_score = (
            float(review_stats['average_review_score'])
            if review_count > 0
            else None
        )

        completion_component = completion_rate * 35
        cancellation_component = max(0.0, 25 - cancellation_rate * 50)
        review_component = ((average_review_score or 4.0) / 5) * 25
        activity_score = min(10.0, (total_orders + published_products) * 1.5)
        popularity_score = min(5.0, published_products * 0.8 + completed_orders * 0.4)
        computed_score = round(
            completion_component
            + cancellation_component
            + review_component
            + activity_score
            + popularity_score
        )
        computed_score = max(0, min(100, computed_score))

        warning_reasons = self._build_warning_reasons(
            total_orders=total_orders,
            completion_rate=completion_rate,
            cancellation_rate=cancellation_rate,
            average_review_score=average_review_score,
            review_count=review_count,
            active_orders=active_orders,
            published_products=published_products,
        )
        risk_level = self._risk_level(computed_score, warning_reasons)

        return CreditAnalysisResponse(
            user_id=user.user_id,
            user_name=user.user_name,
            email=user.email,
            role=user.role,
            base_credit_score=user.credit_score,
            computed_score=computed_score,
            credit_level=self._credit_level(computed_score),
            risk_level=risk_level,
            is_suspicious=risk_level in {'HIGH', 'MEDIUM'},
            warning_reasons=warning_reasons,
            metrics=CreditMetricResponse(
                completed_orders=completed_orders,
                cancelled_orders=cancelled_orders,
                total_orders=total_orders,
                completion_rate=round(completion_rate, 4),
                cancellation_rate=round(cancellation_rate, 4),
                average_review_score=round(average_review_score, 2) if average_review_score is not None else None,
                review_count=review_count,
                published_products=published_products,
                active_orders=active_orders,
                activity_score=round(activity_score, 2),
                popularity_score=round(popularity_score, 2),
            ),
        )

    def _build_warning_reasons(
        self,
        total_orders: int,
        completion_rate: float,
        cancellation_rate: float,
        average_review_score: float | None,
        review_count: int,
        active_orders: int,
        published_products: int,
    ) -> list[str]:
        reasons = []
        if total_orders >= 3 and cancellation_rate >= 0.5:
            reasons.append('订单取消率偏高')
        if total_orders >= 3 and completion_rate < 0.4:
            reasons.append('订单完成率偏低')
        if review_count >= 2 and average_review_score is not None and average_review_score < 3:
            reasons.append('评价均分偏低')
        finished_or_cancelled_orders = total_orders - active_orders
        if active_orders >= 5 and active_orders > max(1, finished_or_cancelled_orders) * 2:
            reasons.append('进行中订单堆积明显')
        if published_products >= 8 and total_orders == 0:
            reasons.append('发布商品较多但缺少交易记录')
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
            'total_orders': 0,
            'completed_orders': 0,
            'cancelled_orders': 0,
            'active_orders': 0,
        }

    def _empty_review_stats(self) -> dict[str, float | int]:
        return {
            'review_count': 0,
            'average_review_score': 0.0,
        }


service = CreditAnalysisService()
