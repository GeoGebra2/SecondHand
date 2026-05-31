from sqlalchemy import select
from sqlalchemy.orm import Session

from app.models.product import Product
from app.models.user import User
from app.schemas.product import ProductCreateRequest, ProductResponse


class ProductService:
    def list_products(self, db: Session) -> list[ProductResponse]:
        rows = db.execute(
            select(Product, User.user_name)
            .join(User, User.user_id == Product.seller_id)
            .order_by(Product.publish_time.desc())
        ).all()
        return [
            ProductResponse(
                product_id=product.product_id,
                seller_id=product.seller_id,
                seller_name=seller_name,
                title=product.title,
                description=product.description,
                price=product.price,
                category_name=product.category_name,
                trade_location=product.trade_location,
                status=product.status,
                publish_time=product.publish_time,
                update_time=product.update_time,
            )
            for product, seller_name in rows
        ]

    def create_product(self, db: Session, user: User, payload: ProductCreateRequest) -> ProductResponse:
        product = Product(
            seller_id=user.user_id,
            title=payload.title,
            description=payload.description,
            price=payload.price,
            category_name=payload.category_name,
            trade_location=payload.trade_location,
            status='ON_SALE',
        )
        db.add(product)
        db.commit()
        db.refresh(product)
        return ProductResponse(
            product_id=product.product_id,
            seller_id=product.seller_id,
            seller_name=user.user_name,
            title=product.title,
            description=product.description,
            price=product.price,
            category_name=product.category_name,
            trade_location=product.trade_location,
            status=product.status,
            publish_time=product.publish_time,
            update_time=product.update_time,
        )


service = ProductService()
