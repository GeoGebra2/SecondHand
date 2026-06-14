from datetime import datetime

from sqlalchemy import DateTime, ForeignKey, String, UniqueConstraint, func
from sqlalchemy.orm import Mapped, mapped_column

from app.db.session import Base
from app.db.types import BIGINT_ID


class Favorite(Base):
    __tablename__ = 'favorite'
    __table_args__ = (UniqueConstraint('user_id', 'product_id', name='uk_favorite_user_product'),)

    favorite_id: Mapped[int] = mapped_column(BIGINT_ID, primary_key=True, autoincrement=True)
    user_id: Mapped[int] = mapped_column(BIGINT_ID, ForeignKey('user.user_id', ondelete='CASCADE'), index=True)
    product_id: Mapped[int] = mapped_column(BIGINT_ID, ForeignKey('product.product_id', ondelete='CASCADE'), index=True)
    create_time: Mapped[datetime] = mapped_column(DateTime, server_default=func.now(), nullable=False)


class Notification(Base):
    __tablename__ = 'notification'

    notification_id: Mapped[int] = mapped_column(BIGINT_ID, primary_key=True, autoincrement=True)
    receiver_id: Mapped[int] = mapped_column(BIGINT_ID, ForeignKey('user.user_id', ondelete='CASCADE'), index=True)
    content: Mapped[str] = mapped_column(String(255))
    create_time: Mapped[datetime] = mapped_column(DateTime, server_default=func.now(), nullable=False)
