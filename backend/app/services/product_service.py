from sqlalchemy import and_, or_, select
from sqlalchemy.orm import Session

from app.models.product import Category, Product, ProductImage
from app.models.user import User
from app.schemas.product import (
    CategoryCreateRequest,
    CategoryResponse,
    CategoryUpdateRequest,
    ProductCreateRequest,
    ProductQueryParams,
    ProductResponse,
    ProductUpdateRequest,
)


class ProductService:
    def list_products(self, db: Session, params: ProductQueryParams) -> list[ProductResponse]:
        statement = (
            select(Product, User.user_name, Category.category_name)
            .join(User, User.user_id == Product.seller_id)
            .join(Category, Category.category_id == Product.category_id)
        )
        filters = []

        if not params.include_offline:
            filters.append(Product.status == 'ON_SALE')
        if params.keyword:
            keyword = f'%{params.keyword}%'
            filters.append(or_(Product.title.like(keyword), Product.description.like(keyword)))
        if params.category_id:
            filters.append(Product.category_id == params.category_id)
        if params.min_price is not None:
            filters.append(Product.price >= params.min_price)
        if params.max_price is not None:
            filters.append(Product.price <= params.max_price)
        if params.min_price is not None and params.max_price is not None and params.min_price > params.max_price:
            raise ValueError('最低价格不能高于最高价格')

        if filters:
            statement = statement.where(and_(*filters))

        sort_column = Product.price if params.sort_by == 'price' else Product.publish_time
        statement = statement.order_by(sort_column.asc() if params.sort_order == 'asc' else sort_column.desc())

        rows = db.execute(statement).all()
        return self._build_product_responses(db, rows)

    def list_my_products(self, db: Session, user: User) -> list[ProductResponse]:
        rows = db.execute(
            select(Product, User.user_name, Category.category_name)
            .join(User, User.user_id == Product.seller_id)
            .join(Category, Category.category_id == Product.category_id)
            .where(Product.seller_id == user.user_id)
            .order_by(Product.publish_time.desc())
        ).all()
        return self._build_product_responses(db, rows)

    def create_product(self, db: Session, user: User, payload: ProductCreateRequest) -> ProductResponse:
        category = self._get_category_or_raise(db, payload.category_id)
        product = Product(
            seller_id=user.user_id,
            title=payload.title,
            description=payload.description,
            price=payload.price,
            category_id=category.category_id,
            trade_location=payload.trade_location,
            status='ON_SALE',
        )
        db.add(product)
        db.flush()
        self._replace_images(db, product.product_id, payload.image_urls)
        db.commit()
        db.refresh(product)
        return self._build_product_response(product, user.user_name, category.category_name, payload.image_urls)

    def update_product(
        self,
        db: Session,
        product_id: int,
        user: User,
        payload: ProductUpdateRequest,
    ) -> ProductResponse:
        product = self._get_owned_product(db, product_id, user)
        if product.status in {'LOCKED', 'SOLD'}:
            raise ValueError('已锁定或已售出的商品不能编辑')

        category = self._get_category_or_raise(db, payload.category_id)
        product.title = payload.title
        product.description = payload.description
        product.price = payload.price
        product.category_id = category.category_id
        product.trade_location = payload.trade_location
        self._replace_images(db, product.product_id, payload.image_urls)
        db.add(product)
        db.commit()
        db.refresh(product)
        return self._build_product_response(product, user.user_name, category.category_name, payload.image_urls)

    def offline_product(self, db: Session, product_id: int, user: User) -> ProductResponse:
        product = self._get_owned_product(db, product_id, user)
        if product.status == 'SOLD':
            raise ValueError('已售出的商品不能下架')
        if product.status == 'LOCKED':
            raise ValueError('已被下单锁定的商品不能下架')

        product.status = 'OFFLINE'
        db.add(product)
        db.commit()
        db.refresh(product)
        image_urls = self._get_image_map(db, [product.product_id]).get(product.product_id, [])
        category_name = self._get_category_name(db, product.category_id)
        return self._build_product_response(product, user.user_name, category_name, image_urls)

    def relist_product(self, db: Session, product_id: int, user: User) -> ProductResponse:
        product = self._get_owned_product(db, product_id, user)
        if product.status != 'OFFLINE':
            raise ValueError('只有已下架商品可以重新上架')

        product.status = 'ON_SALE'
        db.add(product)
        db.commit()
        db.refresh(product)
        image_urls = self._get_image_map(db, [product.product_id]).get(product.product_id, [])
        category_name = self._get_category_name(db, product.category_id)
        return self._build_product_response(product, user.user_name, category_name, image_urls)

    def list_categories(self, db: Session, include_disabled: bool = False) -> list[CategoryResponse]:
        statement = select(Category)
        if not include_disabled:
            statement = statement.where(Category.status == 'ACTIVE')
        categories = db.scalars(statement.order_by(Category.sort_order.asc(), Category.category_name.asc())).all()
        return [CategoryResponse.model_validate(category) for category in categories]

    def create_category(self, db: Session, payload: CategoryCreateRequest) -> CategoryResponse:
        existed = db.scalar(select(Category).where(Category.category_name == payload.category_name))
        if existed is not None:
            raise ValueError('分类名称已存在')

        category = Category(
            category_name=payload.category_name,
            description=payload.description,
            sort_order=payload.sort_order,
            status='ACTIVE',
        )
        db.add(category)
        db.commit()
        db.refresh(category)
        return CategoryResponse.model_validate(category)

    def update_category(self, db: Session, category_id: int, payload: CategoryUpdateRequest) -> CategoryResponse:
        category = db.get(Category, category_id)
        if category is None:
            raise ValueError('分类不存在')

        duplicated = db.scalar(
            select(Category).where(
                Category.category_name == payload.category_name,
                Category.category_id != category_id,
            )
        )
        if duplicated is not None:
            raise ValueError('分类名称已存在')

        category.category_name = payload.category_name
        category.description = payload.description
        category.sort_order = payload.sort_order
        category.status = payload.status
        db.add(category)
        db.commit()
        db.refresh(category)
        return CategoryResponse.model_validate(category)

    def _get_category_or_raise(self, db: Session, category_id: int) -> Category:
        category = db.get(Category, category_id)
        if category is None:
            raise ValueError('商品分类不存在')
        if category.status != 'ACTIVE':
            raise ValueError('该分类已停用')
        return category

    def _get_category_name(self, db: Session, category_id: int) -> str:
        category = db.get(Category, category_id)
        return category.category_name if category else '未知分类'

    def _get_owned_product(self, db: Session, product_id: int, user: User) -> Product:
        product = db.get(Product, product_id)
        if product is None:
            raise ValueError('商品不存在')
        if product.seller_id != user.user_id:
            raise PermissionError('只能管理自己发布的商品')
        return product

    def _replace_images(self, db: Session, product_id: int, image_urls: list[str]) -> None:
        existed_images = db.scalars(select(ProductImage).where(ProductImage.product_id == product_id)).all()
        for image in existed_images:
            db.delete(image)
        for index, image_url in enumerate(image_urls):
            db.add(ProductImage(product_id=product_id, image_url=image_url, sort_order=index))

    def _build_product_responses(
        self,
        db: Session,
        rows: list[tuple[Product, str, str]],
    ) -> list[ProductResponse]:
        product_ids = [product.product_id for product, _, _ in rows]
        image_map = self._get_image_map(db, product_ids)
        return [
            self._build_product_response(product, seller_name, category_name, image_map.get(product.product_id, []))
            for product, seller_name, category_name in rows
        ]

    def _get_image_map(self, db: Session, product_ids: list[int]) -> dict[int, list[str]]:
        if not product_ids:
            return {}
        images = db.scalars(
            select(ProductImage)
            .where(ProductImage.product_id.in_(product_ids))
            .order_by(ProductImage.product_id.asc(), ProductImage.sort_order.asc())
        ).all()
        image_map: dict[int, list[str]] = {}
        for image in images:
            image_map.setdefault(image.product_id, []).append(image.image_url)
        return image_map

    def _build_product_response(
        self,
        product: Product,
        seller_name: str,
        category_name: str,
        image_urls: list[str],
    ) -> ProductResponse:
        return ProductResponse(
            product_id=product.product_id,
            seller_id=product.seller_id,
            seller_name=seller_name,
            title=product.title,
            description=product.description,
            price=product.price,
            category_id=product.category_id,
            category_name=category_name,
            trade_location=product.trade_location,
            status=product.status,
            image_urls=image_urls,
            publish_time=product.publish_time,
            update_time=product.update_time,
        )


service = ProductService()
