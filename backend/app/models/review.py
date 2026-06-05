from datetime import datetime

from sqlalchemy import DateTime, ForeignKey, Integer, String, func
from sqlalchemy.orm import Mapped, mapped_column

from app.db.session import Base
from app.db.types import BIGINT_ID


class Review(Base):
    __tablename__ = 'review'

    review_id: Mapped[int] = mapped_column(BIGINT_ID, primary_key=True, autoincrement=True)
    order_id: Mapped[int] = mapped_column(BIGINT_ID, ForeignKey('order_info.order_id', ondelete='CASCADE'), unique=True)
    reviewer_id: Mapped[int] = mapped_column(BIGINT_ID, ForeignKey('user.user_id', ondelete='CASCADE'))
    reviewed_user_id: Mapped[int] = mapped_column(BIGINT_ID, ForeignKey('user.user_id', ondelete='CASCADE'), index=True)
    score: Mapped[int] = mapped_column(Integer)
    content: Mapped[str] = mapped_column(String(255))
    create_time: Mapped[datetime] = mapped_column(DateTime, server_default=func.now(), nullable=False)
