from datetime import datetime

from sqlalchemy import DateTime, ForeignKey, String, func
from sqlalchemy.orm import Mapped, mapped_column

from app.db.session import Base
from app.db.types import BIGINT_ID


class Notification(Base):
    __tablename__ = 'notification'

    notification_id: Mapped[int] = mapped_column(BIGINT_ID, primary_key=True, autoincrement=True)
    receiver_id: Mapped[int] = mapped_column(BIGINT_ID, ForeignKey('user.user_id', ondelete='CASCADE'), index=True)
    content: Mapped[str] = mapped_column(String(255))
    create_time: Mapped[datetime] = mapped_column(DateTime, server_default=func.now(), nullable=False)
