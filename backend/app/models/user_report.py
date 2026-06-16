from datetime import datetime

from sqlalchemy import DateTime, ForeignKey, String, Text, func
from sqlalchemy.orm import Mapped, mapped_column

from app.db.session import Base
from app.db.types import BIGINT_ID


class UserReport(Base):
    __tablename__ = 'user_report'

    report_id: Mapped[int] = mapped_column(BIGINT_ID, primary_key=True, autoincrement=True)
    reporter_id: Mapped[int] = mapped_column(BIGINT_ID, ForeignKey('user.user_id', ondelete='CASCADE'), index=True)
    reported_user_id: Mapped[int] = mapped_column(BIGINT_ID, ForeignKey('user.user_id', ondelete='CASCADE'), index=True)
    reason: Mapped[str] = mapped_column(String(100))
    description: Mapped[str | None] = mapped_column(Text, nullable=True)
    status: Mapped[str] = mapped_column(String(20), default='PENDING', index=True)
    create_time: Mapped[datetime] = mapped_column(DateTime, server_default=func.now(), nullable=False)
    update_time: Mapped[datetime] = mapped_column(
        DateTime,
        server_default=func.now(),
        onupdate=func.now(),
        nullable=False,
    )
