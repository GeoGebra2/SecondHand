from collections import defaultdict
from math import sqrt
from statistics import mean

from sqlalchemy import func, select
from sqlalchemy.orm import Session

from app.models.order_info import OrderInfo
from app.models.product import Category, Product, ProductImage
from app.models.recommendation import BrowseHistory
from app.models.social import Favorite
from app.models.user import User
from app.schemas.recommendation import RecommendationItem, RecommendationResponse


class RecommendationService:
    def get_recommendations(self, db: Session, user: User | None, limit: int = 6) -> RecommendationResponse:
        products = db.scalars(
            select(Product)
            .where(Product.status == 'ON_SALE')
            .order_by(Product.publish_time.desc())
        ).all()
        if not products:
            return RecommendationResponse(
                algorithm='hybrid-ai-lite-v1',
                profile_summary='当前暂无可推荐商品',
                items=[],
            )

        categories = {
            category.category_id: category
            for category in db.scalars(select(Category)).all()
        }
        users = {
            member.user_id: member
            for member in db.scalars(select(User)).all()
        }
        image_map = self._get_image_map(db, [product.product_id for product in products])
        favorite_counts = self._get_count_map(db, Favorite.product_id, Favorite.favorite_id)
        completed_order_counts = self._get_completed_order_count_map(db)

        if user is None:
            items = self._build_popular_items(products, categories, users, image_map, favorite_counts, completed_order_counts, limit)
            return RecommendationResponse(
                algorithm='hybrid-ai-lite-v1',
                profile_summary='未登录状态下展示平台热门商品推荐',
                items=items,
            )

        behavior = self._build_user_behavior(db, user.user_id)
        user_vectors, user_product_signals = self._build_user_vectors_and_product_signals(db)
        collaborative_scores = self._build_collaborative_scores(user.user_id, user_vectors, user_product_signals)
        avg_price = mean(behavior['price_samples']) if behavior['price_samples'] else None

        candidate_products = [
            product
            for product in products
            if product.seller_id != user.user_id and product.product_id not in behavior['excluded_product_ids']
        ]

        scored_items: list[RecommendationItem] = []
        max_popularity = max(
            ((favorite_counts.get(product.product_id, 0) * 2) + (completed_order_counts.get(product.product_id, 0) * 3) for product in products),
            default=1,
        )

        for product in candidate_products:
            category_weight = behavior['category_weights'].get(product.category_id, 0.0)
            category_score = min(category_weight / 8.0, 1.0)

            price_score = 0.3
            if avg_price is not None:
                distance = abs(float(product.price) - avg_price)
                price_score = max(0.0, 1 - distance / max(avg_price, 1.0))

            popularity_raw = (favorite_counts.get(product.product_id, 0) * 2) + (completed_order_counts.get(product.product_id, 0) * 3)
            popularity_score = popularity_raw / max_popularity if max_popularity else 0.0

            collaborative_score = collaborative_scores.get(product.product_id, 0.0)

            ai_score = round(
                category_score * 0.45
                + price_score * 0.2
                + popularity_score * 0.2
                + collaborative_score * 0.15,
                4,
            )
            if ai_score <= 0:
                continue

            reason, tags = self._build_reason(
                product=product,
                categories=categories,
                behavior=behavior,
                category_score=category_score,
                price_score=price_score,
                popularity_score=popularity_score,
                collaborative_score=collaborative_score,
            )

            seller_name = users.get(product.seller_id).user_name if users.get(product.seller_id) else '未知卖家'
            category_name = categories.get(product.category_id).category_name if categories.get(product.category_id) else '未知分类'
            scored_items.append(
                RecommendationItem(
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
                    image_urls=image_map.get(product.product_id, []),
                    publish_time=product.publish_time,
                    update_time=product.update_time,
                    ai_score=ai_score,
                    ai_reason=reason,
                    ai_tags=tags,
                )
            )

        scored_items.sort(key=lambda item: (item.ai_score, item.publish_time), reverse=True)

        profile_parts = []
        preferred_categories = sorted(
            behavior['category_weights'].items(),
            key=lambda item: item[1],
            reverse=True,
        )[:2]
        if preferred_categories:
            labels = [categories[category_id].category_name for category_id, _ in preferred_categories if category_id in categories]
            if labels:
                profile_parts.append(f"偏好类别：{'、'.join(labels)}")
        if avg_price is not None:
            profile_parts.append(f'常见价格区间约 {avg_price:.0f} 元')
        if not profile_parts:
            profile_parts.append('行为数据较少，当前结合平台热门度进行冷启动推荐')

        return RecommendationResponse(
            algorithm='hybrid-ai-lite-v1',
            profile_summary='；'.join(profile_parts),
            items=scored_items[:limit],
        )

    def record_browse_history(self, db: Session, user: User, product_ids: list[int]) -> int:
        valid_ids = {
            product_id
            for product_id in product_ids
            if db.get(Product, product_id) is not None
        }
        for product_id in valid_ids:
            db.add(BrowseHistory(user_id=user.user_id, product_id=product_id))
        db.commit()
        return len(valid_ids)

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

    def _get_count_map(self, db: Session, group_column, count_column) -> dict[int, int]:
        return {
            key: count
            for key, count in db.execute(
                select(group_column, func.count(count_column)).group_by(group_column)
            ).all()
        }

    def _get_completed_order_count_map(self, db: Session) -> dict[int, int]:
        return {
            product_id: count
            for product_id, count in db.execute(
                select(OrderInfo.product_id, func.count(OrderInfo.order_id))
                .where(OrderInfo.order_status == 'COMPLETED')
                .group_by(OrderInfo.product_id)
            ).all()
        }

    def _build_popular_items(
        self,
        products: list[Product],
        categories: dict[int, Category],
        users: dict[int, User],
        image_map: dict[int, list[str]],
        favorite_counts: dict[int, int],
        completed_order_counts: dict[int, int],
        limit: int,
    ) -> list[RecommendationItem]:
        ranked = []
        for product in products:
            popularity_score = favorite_counts.get(product.product_id, 0) * 2 + completed_order_counts.get(product.product_id, 0) * 3
            category_name = categories.get(product.category_id).category_name if categories.get(product.category_id) else '未知分类'
            seller_name = users.get(product.seller_id).user_name if users.get(product.seller_id) else '未知卖家'
            ranked.append(
                RecommendationItem(
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
                    image_urls=image_map.get(product.product_id, []),
                    publish_time=product.publish_time,
                    update_time=product.update_time,
                    ai_score=float(popularity_score),
                    ai_reason='基于平台热门度、成交量和收藏量生成的冷启动推荐',
                    ai_tags=['热门商品', '冷启动推荐'],
                )
            )
        ranked.sort(key=lambda item: (item.ai_score, item.publish_time), reverse=True)
        return ranked[:limit]

    def _build_user_behavior(self, db: Session, user_id: int) -> dict[str, object]:
        category_weights: dict[int, float] = defaultdict(float)
        price_samples: list[float] = []
        excluded_product_ids: set[int] = set()

        favorite_rows = db.execute(
            select(Favorite.product_id, Product.category_id, Product.price)
            .join(Product, Product.product_id == Favorite.product_id)
            .where(Favorite.user_id == user_id)
        ).all()
        for product_id, category_id, price in favorite_rows:
            excluded_product_ids.add(product_id)
            category_weights[category_id] += 3.0
            price_samples.append(float(price))

        order_rows = db.execute(
            select(OrderInfo.product_id, Product.category_id, Product.price, OrderInfo.order_status)
            .join(Product, Product.product_id == OrderInfo.product_id)
            .where(OrderInfo.buyer_id == user_id)
        ).all()
        for product_id, category_id, price, order_status in order_rows:
            excluded_product_ids.add(product_id)
            category_weights[category_id] += 4.0 if order_status == 'COMPLETED' else 2.0
            price_samples.append(float(price))

        browse_rows = db.execute(
            select(BrowseHistory.product_id, Product.category_id, Product.price)
            .join(Product, Product.product_id == BrowseHistory.product_id)
            .where(BrowseHistory.user_id == user_id)
        ).all()
        for _, category_id, price in browse_rows:
            category_weights[category_id] += 1.5
            price_samples.append(float(price))

        return {
            'category_weights': dict(category_weights),
            'price_samples': price_samples,
            'excluded_product_ids': excluded_product_ids,
        }

    def _build_user_vectors_and_product_signals(
        self,
        db: Session,
    ) -> tuple[dict[int, dict[int, float]], dict[int, dict[int, float]]]:
        vectors: dict[int, dict[int, float]] = defaultdict(lambda: defaultdict(float))
        product_signals: dict[int, dict[int, float]] = defaultdict(lambda: defaultdict(float))

        favorite_rows = db.execute(
            select(Favorite.user_id, Favorite.product_id, Product.category_id)
            .join(Product, Product.product_id == Favorite.product_id)
        ).all()
        for user_id, product_id, category_id in favorite_rows:
            vectors[user_id][category_id] += 3.0
            product_signals[user_id][product_id] += 3.0

        order_rows = db.execute(
            select(OrderInfo.buyer_id, OrderInfo.product_id, Product.category_id, OrderInfo.order_status)
            .join(Product, Product.product_id == OrderInfo.product_id)
        ).all()
        for user_id, product_id, category_id, order_status in order_rows:
            weight = 4.0 if order_status == 'COMPLETED' else 2.0
            vectors[user_id][category_id] += weight
            product_signals[user_id][product_id] += weight

        browse_rows = db.execute(
            select(BrowseHistory.user_id, BrowseHistory.product_id, Product.category_id)
            .join(Product, Product.product_id == BrowseHistory.product_id)
        ).all()
        for user_id, product_id, category_id in browse_rows:
            vectors[user_id][category_id] += 1.5
            product_signals[user_id][product_id] += 1.5

        return (
            {user_id: dict(vector) for user_id, vector in vectors.items()},
            {user_id: dict(signal_map) for user_id, signal_map in product_signals.items()},
        )

    def _build_collaborative_scores(
        self,
        current_user_id: int,
        user_vectors: dict[int, dict[int, float]],
        user_product_signals: dict[int, dict[int, float]],
    ) -> dict[int, float]:
        current_vector = user_vectors.get(current_user_id, {})
        if not current_vector:
            return {}

        similarity_scores: dict[int, float] = {}
        for other_user_id, other_vector in user_vectors.items():
            if other_user_id == current_user_id:
                continue
            similarity = self._cosine_similarity(current_vector, other_vector)
            if similarity > 0:
                similarity_scores[other_user_id] = similarity

        collaborative_scores: dict[int, float] = defaultdict(float)
        for other_user_id, similarity in similarity_scores.items():
            for product_id, signal_weight in user_product_signals.get(other_user_id, {}).items():
                collaborative_scores[product_id] += similarity * signal_weight

        if not collaborative_scores:
            return {}

        max_score = max(collaborative_scores.values())
        return {product_id: score / max_score for product_id, score in collaborative_scores.items()}

    def _build_reason(
        self,
        product: Product,
        categories: dict[int, Category],
        behavior: dict[str, object],
        category_score: float,
        price_score: float,
        popularity_score: float,
        collaborative_score: float,
    ) -> tuple[str, list[str]]:
        category_name = categories.get(product.category_id).category_name if categories.get(product.category_id) else '该分类'
        tags: list[str] = []
        reason_parts: list[str] = []

        if category_score >= 0.45:
            reason_parts.append(f'你的历史收藏、浏览或下单行为显示你偏好 {category_name}')
            tags.append('类别偏好匹配')
        if price_score >= 0.65:
            reason_parts.append('该商品价格与你常浏览或购买的价格区间相近')
            tags.append('价格相似')
        if popularity_score >= 0.45:
            reason_parts.append('该商品在平台内收藏量和成交热度较高')
            tags.append('热门商品')
        if collaborative_score >= 0.35:
            reason_parts.append('与您兴趣相近的用户也偏好这类商品')
            tags.append('协同过滤')

        if not reason_parts:
            reason_parts.append('系统根据平台热度和基础行为特征进行智能冷启动推荐')
            tags.append('冷启动推荐')

        return '；'.join(reason_parts), tags

    def _cosine_similarity(self, left: dict[int, float], right: dict[int, float]) -> float:
        if not left or not right:
            return 0.0
        shared_keys = set(left) | set(right)
        dot = sum(left.get(key, 0.0) * right.get(key, 0.0) for key in shared_keys)
        left_norm = sqrt(sum(value * value for value in left.values()))
        right_norm = sqrt(sum(value * value for value in right.values()))
        if left_norm == 0 or right_norm == 0:
            return 0.0
        return dot / (left_norm * right_norm)


service = RecommendationService()
