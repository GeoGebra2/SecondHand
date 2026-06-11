from collections import defaultdict
from datetime import datetime

from sqlalchemy import func, select
from sqlalchemy.orm import Session

from app.models.order_info import OrderInfo
from app.models.product import Category, Product
from app.models.social import Favorite, Notification
from app.models.user import User
from app.schemas.social import (
    ActiveUserItem,
    CategoryHeatmapItem,
    DashboardStatsResponse,
    FavoriteResponse,
    NotificationResponse,
    TradeTrendItem,
)


class SocialService:
    def add_favorite(self, db: Session, user: User, product_id: int) -> None:
        product = db.get(Product, product_id)
        if product is None:
            raise ValueError('商品不存在')
        if product.seller_id == user.user_id:
            raise ValueError('不能收藏自己发布的商品')

        existing = db.scalar(
            select(Favorite).where(
                Favorite.user_id == user.user_id,
                Favorite.product_id == product_id,
            )
        )
        if existing is not None:
            raise ValueError('您已经收藏过该商品')

        db.add(Favorite(user_id=user.user_id, product_id=product_id))
        db.commit()

    def list_favorites(self, db: Session, user: User) -> list[FavoriteResponse]:
        rows = db.execute(
            select(Favorite, Product.title, Category.category_name)
            .join(Product, Product.product_id == Favorite.product_id)
            .join(Category, Category.category_id == Product.category_id)
            .where(Favorite.user_id == user.user_id)
            .order_by(Favorite.create_time.desc())
        ).all()
        return [
            FavoriteResponse(
                favorite_id=favorite.favorite_id,
                product_id=favorite.product_id,
                product_title=title,
                category_name=category_name,
                create_time=favorite.create_time,
            )
            for favorite, title, category_name in rows
        ]

    def create_notification(self, db: Session, receiver_id: int, content: str) -> NotificationResponse:
        receiver = db.get(User, receiver_id)
        if receiver is None:
            raise ValueError('接收用户不存在')

        notification = Notification(receiver_id=receiver_id, content=content)
        db.add(notification)
        db.commit()
        db.refresh(notification)
        return NotificationResponse.model_validate(notification)

    def list_notifications(self, db: Session, user: User) -> list[NotificationResponse]:
        notifications = db.scalars(
            select(Notification)
            .where(Notification.receiver_id == user.user_id)
            .order_by(Notification.create_time.desc())
        ).all()
        return [NotificationResponse.model_validate(item) for item in notifications]

    def get_dashboard_stats(self, db: Session) -> DashboardStatsResponse:
        category_rows = db.execute(
            select(
                Category.category_id,
                Category.category_name,
                func.count(func.distinct(Product.product_id)).label('pub_count'),
                func.coalesce(func.sum(func.distinct(Product.price)), 0).label('total_revenue'),
                func.count(Favorite.favorite_id).label('fav_count'),
            )
            .select_from(Category)
            .join(Product, Product.category_id == Category.category_id, isouter=True)
            .join(Favorite, Favorite.product_id == Product.product_id, isouter=True)
            .group_by(Category.category_id, Category.category_name)
            .order_by(Category.category_name.asc())
        ).all()

        categories = [
            CategoryHeatmapItem(
                category_id=category_id,
                category_name=category_name,
                sales_count=int((pub_count or 0) + (fav_count or 0)),
                total_revenue=int(total_revenue or 0),
            )
            for category_id, category_name, pub_count, total_revenue, fav_count in category_rows
        ]
        categories.sort(key=lambda item: item.sales_count, reverse=True)

        users = self._build_active_users(db)

        trend_rows = db.execute(
            select(OrderInfo.finish_time, OrderInfo.order_amount)
            .where(
                OrderInfo.order_status == 'COMPLETED',
                OrderInfo.finish_time.is_not(None),
            )
            .order_by(OrderInfo.finish_time.asc())
        ).all()
        trend_map: dict[str, int] = defaultdict(int)
        for finish_time, order_amount in trend_rows:
            if finish_time is None:
                continue
            label = self._format_date_label(finish_time)
            trend_map[label] += int(order_amount or 0)
        trends = [TradeTrendItem(date=label, amount=amount) for label, amount in sorted(trend_map.items())]

        pending_product_count = db.scalar(select(func.count()).select_from(Product).where(Product.status == 'OFFLINE')) or 0
        category_count = db.scalar(select(func.count()).select_from(Category).where(Category.status == 'ACTIVE')) or 0
        recommendation_heat = '高' if sum(item.sales_count for item in categories[:3]) >= 10 else '中'

        return DashboardStatsResponse(
            pending_product_count=int(pending_product_count),
            category_count=int(category_count),
            recommendation_heat=recommendation_heat,
            categories=categories,
            users=users,
            trends=trends,
        )

    def _format_date_label(self, value: datetime) -> str:
        return value.strftime('%m-%d')

    def _build_active_users(self, db: Session) -> list[ActiveUserItem]:
        users = db.scalars(select(User).order_by(User.user_id.asc())).all()
        if not users:
            return []

        product_counts = {
            user_id: count
            for user_id, count in db.execute(
                select(Product.seller_id, func.count(Product.product_id))
                .group_by(Product.seller_id)
            ).all()
        }
        favorite_counts = {
            user_id: count
            for user_id, count in db.execute(
                select(Favorite.user_id, func.count(Favorite.favorite_id))
                .group_by(Favorite.user_id)
            ).all()
        }

        now = datetime.now()
        ranked = []
        for user in users:
            recent_bonus = 0
            if user.last_login_time is not None:
                last_login = user.last_login_time.replace(tzinfo=None) if user.last_login_time.tzinfo else user.last_login_time
                if (now - last_login).days <= 7:
                    recent_bonus = 50
            action_count = product_counts.get(user.user_id, 0) * 20 + favorite_counts.get(user.user_id, 0) * 10 + recent_bonus
            ranked.append(ActiveUserItem(user_name=user.user_name, action_count=int(action_count)))

        ranked.sort(key=lambda item: item.action_count, reverse=True)
        return ranked[:5]


service = SocialService()
