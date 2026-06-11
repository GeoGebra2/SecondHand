from datetime import datetime

from sqlalchemy import DateTime, ForeignKey, func
from sqlalchemy.orm import Mapped, mapped_column

from app.db.session import Base
from app.db.types import BIGINT_ID


class BrowseHistory(Base):
    __tablename__ = 'browse_history'

    history_id: Mapped[int] = mapped_column(BIGINT_ID, primary_key=True, autoincrement=True)
    user_id: Mapped[int] = mapped_column(BIGINT_ID, ForeignKey('user.user_id', ondelete='CASCADE'), index=True)
    product_id: Mapped[int] = mapped_column(BIGINT_ID, ForeignKey('product.product_id', ondelete='CASCADE'), index=True)
    browse_time: Mapped[datetime] = mapped_column(DateTime, server_default=func.now(), nullable=False)
