from datetime import datetime
from decimal import Decimal

from sqlalchemy import DateTime, ForeignKey, Numeric, String, Text, func
from sqlalchemy.orm import Mapped, mapped_column

from app.db.session import Base


class Product(Base):
    __tablename__ = 'product'

    product_id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    seller_id: Mapped[int] = mapped_column(ForeignKey('user.user_id', ondelete='CASCADE'), index=True)
    title: Mapped[str] = mapped_column(String(100))
    description: Mapped[str | None] = mapped_column(Text, nullable=True)
    price: Mapped[Decimal] = mapped_column(Numeric(10, 2))
    category_name: Mapped[str] = mapped_column(String(50))
    trade_location: Mapped[str] = mapped_column(String(100))
    status: Mapped[str] = mapped_column(String(20), default='ON_SALE', index=True)
    publish_time: Mapped[datetime] = mapped_column(DateTime, server_default=func.now(), nullable=False)
    update_time: Mapped[datetime] = mapped_column(
        DateTime,
        server_default=func.now(),
        onupdate=func.now(),
        nullable=False,
    )
