from datetime import datetime
from decimal import Decimal

from sqlalchemy import DateTime, ForeignKey, Integer, Numeric, String, Text, func
from sqlalchemy.orm import Mapped, mapped_column

from app.db.session import Base


class Category(Base):
    __tablename__ = 'category'

    category_id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    category_name: Mapped[str] = mapped_column(String(50), unique=True, index=True)
    description: Mapped[str | None] = mapped_column(String(255), nullable=True)
    sort_order: Mapped[int] = mapped_column(Integer, default=0)
    status: Mapped[str] = mapped_column(String(20), default='ACTIVE', index=True)
    create_time: Mapped[datetime] = mapped_column(DateTime, server_default=func.now(), nullable=False)
    update_time: Mapped[datetime] = mapped_column(
        DateTime,
        server_default=func.now(),
        onupdate=func.now(),
        nullable=False,
    )


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


class ProductImage(Base):
    __tablename__ = 'product_image'

    image_id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    product_id: Mapped[int] = mapped_column(ForeignKey('product.product_id', ondelete='CASCADE'), index=True)
    image_url: Mapped[str] = mapped_column(String(500))
    sort_order: Mapped[int] = mapped_column(Integer, default=0)
    create_time: Mapped[datetime] = mapped_column(DateTime, server_default=func.now(), nullable=False)
