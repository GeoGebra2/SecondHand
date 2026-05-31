from sqlalchemy import select
from sqlalchemy.orm import Session, aliased

from app.models.review import Review
from app.models.user import User
from app.schemas.review import ReviewCreateRequest, ReviewResponse
from app.services.order_service import service as order_service


class ReviewService:
    def _build_review_query(self):
        reviewer = aliased(User)
        reviewed_user = aliased(User)
        return (
            select(
                Review.review_id,
                Review.order_id,
                Review.reviewer_id,
                reviewer.user_name.label('reviewer_name'),
                Review.reviewed_user_id,
                reviewed_user.user_name.label('reviewed_user_name'),
                Review.score,
                Review.content,
                Review.create_time,
            )
            .join(reviewer, reviewer.user_id == Review.reviewer_id)
            .join(reviewed_user, reviewed_user.user_id == Review.reviewed_user_id)
        )

    def get_review_response(self, db: Session, review_id: int) -> ReviewResponse:
        row = db.execute(self._build_review_query().where(Review.review_id == review_id)).mappings().first()
        if row is None:
            raise ValueError('评价记录不存在')
        return ReviewResponse.model_validate(row)

    def create_review(self, db: Session, reviewer: User, payload: ReviewCreateRequest) -> ReviewResponse:
        order = order_service.get_order(db, payload.order_id)
        if reviewer.user_id != order.buyer_id:
            raise PermissionError('只有买家可以提交评价')
        if order.order_status != 'COMPLETED':
            raise ValueError('只有已完成订单才可以评价')

        existing_review = db.scalar(select(Review).where(Review.order_id == order.order_id))
        if existing_review:
            raise ValueError('该订单已经评价过了')

        review = Review(
            order_id=order.order_id,
            reviewer_id=reviewer.user_id,
            reviewed_user_id=order.seller_id,
            score=payload.score,
            content=payload.content,
        )

        reviewed_user = db.get(User, order.seller_id)
        if reviewed_user is None:
            raise ValueError('被评价用户不存在')

        reviewed_user.credit_score = max(0, min(200, reviewed_user.credit_score + payload.score - 3))

        db.add(review)
        db.add(reviewed_user)
        db.commit()
        db.refresh(review)
        return self.get_review_response(db, review.review_id)

    def list_order_reviews(self, db: Session, order_id: int) -> list[ReviewResponse]:
        reviews = db.execute(
            self._build_review_query()
            .where(Review.order_id == order_id)
            .order_by(Review.create_time.desc())
        ).mappings().all()
        return [ReviewResponse.model_validate(review) for review in reviews]


service = ReviewService()
