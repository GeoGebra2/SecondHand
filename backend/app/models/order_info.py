from datetime import datetime
from decimal import Decimal

from sqlalchemy import DateTime, ForeignKey, Numeric, String, func
from sqlalchemy.orm import Mapped, mapped_column

from app.db.session import Base


class OrderInfo(Base):
    __tablename__ = 'order_info'

    order_id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    product_id: Mapped[int] = mapped_column(ForeignKey('product.product_id', ondelete='CASCADE'), index=True)
    buyer_id: Mapped[int] = mapped_column(ForeignKey('user.user_id', ondelete='CASCADE'), index=True)
    seller_id: Mapped[int] = mapped_column(ForeignKey('user.user_id', ondelete='CASCADE'), index=True)
    order_amount: Mapped[Decimal] = mapped_column(Numeric(10, 2))
    order_status: Mapped[str] = mapped_column(String(20), default='PENDING', index=True)
    trade_method: Mapped[str] = mapped_column(String(20), default='offline')
    trade_location: Mapped[str] = mapped_column(String(100))
    buyer_note: Mapped[str | None] = mapped_column(String(255), nullable=True)
    cancel_reason: Mapped[str | None] = mapped_column(String(255), nullable=True)
    create_time: Mapped[datetime] = mapped_column(DateTime, server_default=func.now(), nullable=False)
    update_time: Mapped[datetime] = mapped_column(
        DateTime,
        server_default=func.now(),
        onupdate=func.now(),
        nullable=False,
    )
    finish_time: Mapped[datetime | None] = mapped_column(DateTime, nullable=True)
