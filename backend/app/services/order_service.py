from datetime import datetime, timezone

from sqlalchemy import or_, select
from sqlalchemy.orm import Session

from app.models.order_info import OrderInfo
from app.models.notification import Notification
from app.models.product import Product
from app.models.review import Review
from app.models.user import User
from app.schemas.credit import UserRiskProfileResponse
from app.schemas.order import OrderCreateRequest, OrderResponse, OrderStatusResponse
from app.services.credit_service import service as credit_service


class OrderService:
    def list_orders(self, db: Session, user: User) -> list[OrderResponse]:
        orders = db.scalars(
            select(OrderInfo)
            .where(or_(OrderInfo.buyer_id == user.user_id, OrderInfo.seller_id == user.user_id))
            .order_by(OrderInfo.create_time.desc())
        ).all()

        if not orders:
            return []

        product_ids = {order.product_id for order in orders}
        user_ids = {order.buyer_id for order in orders} | {order.seller_id for order in orders}
        user_ids.update(order.cancel_user_id for order in orders if order.cancel_user_id is not None)
        reviewed_order_ids = set(
            db.scalars(select(Review.order_id).where(Review.order_id.in_([order.order_id for order in orders]))).all()
        )
        products = {
            product.product_id: product
            for product in db.scalars(select(Product).where(Product.product_id.in_(product_ids))).all()
        }
        users = {
            member.user_id: member
            for member in db.scalars(select(User).where(User.user_id.in_(user_ids))).all()
        }

        seller_risk_profiles = {
            seller_id: credit_service.get_user_risk_profile(db, seller_id)
            for seller_id in {order.seller_id for order in orders}
        }

        return [
            self._build_order_response(order, products, users, reviewed_order_ids, user, seller_risk_profiles)
            for order in orders
        ]

    def create_order(self, db: Session, buyer: User, payload: OrderCreateRequest) -> OrderResponse:
        product = db.get(Product, payload.product_id)
        if product is None:
            raise ValueError('商品不存在')
        if product.seller_id == buyer.user_id:
            raise ValueError('不能购买自己发布的商品')
        if product.status != 'ON_SALE':
            raise ValueError('当前商品不可下单')

        seller = db.get(User, product.seller_id)
        if seller is None or seller.status != 'active':
            raise ValueError('卖家当前不可交易')

        order = OrderInfo(
            product_id=product.product_id,
            buyer_id=buyer.user_id,
            seller_id=product.seller_id,
            order_amount=product.price,
            order_status='PENDING',
            trade_method='offline',
            trade_location=product.trade_location,
            buyer_note=payload.buyer_note,
        )
        notification = Notification(
            receiver_id=seller.user_id,
            content=f'有同学对你发布的商品《{product.title}》下单，请及时确认接单。',
        )
        product.status = 'LOCKED'
        db.add(order)
        db.add(notification)
        db.add(product)
        db.commit()
        db.refresh(order)
        db.refresh(product)
        # 发送站内通知给卖家，告知商品被下单
        try:
            seller = db.get(User, product.seller_id)
            if seller is not None:
                content = f'您的商品 "{product.title}" 有新的订单（买家：{buyer.user_name}），请及时处理。'
                try:
                    social_service.create_notification(db, seller.user_id, content)
                except Exception as exc:
                    # print to server logs to help debugging notification failures
                    print(f'Failed to create notification for seller={seller.user_id}:', exc)
        except Exception as exc:
            print('Unexpected error while attempting to notify seller:', exc)
        return self._build_order_response(
            order,
            {product.product_id: product},
            {buyer.user_id: buyer, seller.user_id: seller},
            set(),
            buyer,
            {seller.user_id: credit_service.get_user_risk_profile(db, seller.user_id)},
        )

    def confirm_order(self, db: Session, order_id: int, user: User) -> OrderStatusResponse:
        order = self._get_order_or_raise(db, order_id)
        if order.seller_id != user.user_id:
            raise PermissionError('只有卖家可以确认订单')
        if order.order_status != 'PENDING':
            raise ValueError('当前订单状态无法确认')

        order.order_status = 'IN_PROGRESS'
        db.add(order)
        db.commit()
        product = self._get_product_or_raise(db, order.product_id)
        # 通知买家：卖家已确认接单
        try:
            buyer = db.get(User, order.buyer_id)
            seller = db.get(User, order.seller_id)
            if buyer is not None and seller is not None:
                content = f'卖家 {seller.user_name} 已确认您的订单（商品：{product.title}）。'
                try:
                    social_service.create_notification(db, buyer.user_id, content)
                except Exception as exc:
                    print(f'Failed to create notification for buyer={buyer.user_id}:', exc)
        except Exception as exc:
            print('Unexpected error while attempting to notify buyer on confirm:', exc)
        return OrderStatusResponse(
            order_id=order.order_id,
            order_status=order.order_status,
            product_status=product.status,
        )

    def complete_order(self, db: Session, order_id: int, user: User) -> OrderStatusResponse:
        order = self._get_order_or_raise(db, order_id)
        if order.buyer_id != user.user_id:
            raise PermissionError('只有买家可以确认成交')
        if order.order_status != 'IN_PROGRESS':
            raise ValueError('当前订单状态无法完成')

        product = self._get_product_or_raise(db, order.product_id)
        order.order_status = 'COMPLETED'
        order.finish_time = datetime.now(timezone.utc)
        product.status = 'SOLD'
        db.add(order)
        db.add(product)
        db.commit()
        return OrderStatusResponse(
            order_id=order.order_id,
            order_status=order.order_status,
            product_status=product.status,
        )

    def cancel_order(self, db: Session, order_id: int, user: User, cancel_reason: str | None) -> OrderStatusResponse:
        order = self._get_order_or_raise(db, order_id)
        if user.user_id not in {order.buyer_id, order.seller_id}:
            raise PermissionError('只有交易双方可以取消订单')
        if order.order_status in {'COMPLETED', 'CANCELLED'}:
            raise ValueError('当前订单不可取消')

        product = self._get_product_or_raise(db, order.product_id)
        previous_status = order.order_status
        order.order_status = 'CANCELLED'
        order.cancel_reason = cancel_reason or '用户主动取消订单'
        order.cancel_user_id = user.user_id if previous_status == 'IN_PROGRESS' else None
        product.status = 'ON_SALE'
        db.add(order)
        db.add(product)
        db.commit()
        return OrderStatusResponse(
            order_id=order.order_id,
            order_status=order.order_status,
            product_status=product.status,
        )

    def get_order(self, db: Session, order_id: int) -> OrderInfo:
        return self._get_order_or_raise(db, order_id)

    def _get_order_or_raise(self, db: Session, order_id: int) -> OrderInfo:
        order = db.get(OrderInfo, order_id)
        if order is None:
            raise ValueError('订单不存在')
        return order

    def _get_product_or_raise(self, db: Session, product_id: int) -> Product:
        product = db.get(Product, product_id)
        if product is None:
            raise ValueError('商品不存在')
        return product

    def _build_order_response(
        self,
        order: OrderInfo,
        products: dict[int, Product],
        users: dict[int, User],
        reviewed_order_ids: set[int],
        current_user: User,
        seller_risk_profiles: dict[int, UserRiskProfileResponse] | None = None,
    ) -> OrderResponse:
        product = products[order.product_id]
        buyer = users[order.buyer_id]
        seller = users[order.seller_id]
        return OrderResponse(
            order_id=order.order_id,
            product_id=order.product_id,
            product_title=product.title,
            buyer_id=order.buyer_id,
            buyer_name=buyer.user_name,
            seller_id=order.seller_id,
            seller_name=seller.user_name,
            order_amount=order.order_amount,
            order_status=order.order_status,
            trade_method=order.trade_method,
            trade_location=order.trade_location,
            buyer_note=order.buyer_note,
            cancel_reason=order.cancel_reason,
            cancel_user_id=order.cancel_user_id,
            cancel_user_name=users[order.cancel_user_id].user_name if order.cancel_user_id else None,
            create_time=order.create_time,
            update_time=order.update_time,
            finish_time=order.finish_time,
            can_review=(
                current_user.user_id == order.buyer_id
                and order.order_status == 'COMPLETED'
                and order.order_id not in reviewed_order_ids
            ),
            seller_risk_profile=(seller_risk_profiles or {}).get(order.seller_id),
        )


service = OrderService()
