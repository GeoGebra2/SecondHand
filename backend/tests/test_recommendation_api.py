from decimal import Decimal

from app.core.security import hash_password
from app.models.order_info import OrderInfo
from app.models.product import Category, Product
from app.models.recommendation import BrowseHistory
from app.models.social import Favorite
from app.models.user import User


def create_user(db_session, **overrides):
    payload = {
        'student_no': '2023007001',
        'user_name': '推荐测试用户',
        'gender': '男',
        'phone': '13800007001',
        'email': 'recommend-user@test.com',
        'password_hash': hash_password('student123'),
        'role': 'student',
        'credit_score': 100,
        'status': 'active',
        'verify_status': 'verified',
    }
    payload.update(overrides)
    user = User(**payload)
    db_session.add(user)
    db_session.commit()
    db_session.refresh(user)
    return user


def create_category(db_session, **overrides):
    payload = {
        'category_name': '教材资料',
        'description': '教材与复习资料',
        'sort_order': 1,
        'status': 'ACTIVE',
    }
    payload.update(overrides)
    category = Category(**payload)
    db_session.add(category)
    db_session.commit()
    db_session.refresh(category)
    return category


def create_product(db_session, seller_id, category_id, **overrides):
    payload = {
        'seller_id': seller_id,
        'category_id': category_id,
        'title': '数据库教材',
        'description': '适合期末复习',
        'price': Decimal('35.00'),
        'trade_location': '图书馆门口',
        'status': 'ON_SALE',
    }
    payload.update(overrides)
    product = Product(**payload)
    db_session.add(product)
    db_session.commit()
    db_session.refresh(product)
    return product


def create_completed_order(db_session, product, buyer_id, seller_id, **overrides):
    payload = {
        'product_id': product.product_id,
        'buyer_id': buyer_id,
        'seller_id': seller_id,
        'order_amount': product.price,
        'order_status': 'COMPLETED',
        'trade_method': 'offline',
        'trade_location': product.trade_location,
        'buyer_note': '推荐测试订单',
    }
    payload.update(overrides)
    order = OrderInfo(**payload)
    db_session.add(order)
    db_session.commit()
    db_session.refresh(order)
    return order


def login_and_get_headers(client, account, password='student123'):
    response = client.post('/api/auth/login', json={'account': account, 'password': password})
    token = response.json()['data']['access_token']
    return {'Authorization': f'Bearer {token}'}


def test_get_recommendations_for_guest_returns_popular_items(client, db_session):
    seller = create_user(
        db_session,
        student_no='2023007002',
        email='recommend-seller@test.com',
        phone='13800007002',
    )
    buyer = create_user(
        db_session,
        student_no='2023007003',
        email='recommend-buyer@test.com',
        phone='13800007003',
    )
    category = create_category(db_session)
    popular_product = create_product(db_session, seller.user_id, category.category_id, title='热门高数教材')
    create_product(db_session, seller.user_id, category.category_id, title='普通英语教材', price=Decimal('20.00'))

    db_session.add(Favorite(user_id=buyer.user_id, product_id=popular_product.product_id))
    db_session.commit()
    create_completed_order(db_session, popular_product, buyer.user_id, seller.user_id)

    response = client.get('/api/recommendations')

    assert response.status_code == 200
    data = response.json()['data']
    assert data['algorithm'] == 'hybrid-ai-lite-v1'
    assert data['profile_summary'] == '未登录状态下展示平台热门商品推荐'
    assert data['items'][0]['title'] == '热门高数教材'
    assert '冷启动推荐' in data['items'][0]['ai_tags']


def test_get_recommendations_for_user_returns_personalized_items(client, db_session):
    seller = create_user(
        db_session,
        student_no='2023007004',
        email='recommend-seller-2@test.com',
        phone='13800007004',
    )
    current_user = create_user(db_session)
    similar_user = create_user(
        db_session,
        student_no='2023007005',
        email='similar-user@test.com',
        phone='13800007005',
    )

    books = create_category(db_session)
    digital = create_category(
        db_session,
        category_name='数码产品',
        description='电子设备',
        sort_order=2,
    )

    favorite_target = create_product(
        db_session,
        seller.user_id,
        books.category_id,
        title='数据库系统教材',
        price=Decimal('36.00'),
    )
    recommended_product = create_product(
        db_session,
        seller.user_id,
        books.category_id,
        title='离散数学复习笔记',
        price=Decimal('34.00'),
    )
    create_product(
        db_session,
        seller.user_id,
        digital.category_id,
        title='蓝牙耳机',
        price=Decimal('189.00'),
    )

    db_session.add(Favorite(user_id=current_user.user_id, product_id=favorite_target.product_id))
    db_session.add(BrowseHistory(user_id=current_user.user_id, product_id=favorite_target.product_id))
    db_session.add(Favorite(user_id=similar_user.user_id, product_id=favorite_target.product_id))
    db_session.add(Favorite(user_id=similar_user.user_id, product_id=recommended_product.product_id))
    db_session.add(BrowseHistory(user_id=similar_user.user_id, product_id=recommended_product.product_id))
    db_session.commit()

    headers = login_and_get_headers(client, current_user.student_no)
    response = client.get('/api/recommendations', headers=headers)

    assert response.status_code == 200
    data = response.json()['data']
    assert data['algorithm'] == 'hybrid-ai-lite-v1'
    assert '偏好类别：教材资料' in data['profile_summary']
    assert data['items']
    top_item = data['items'][0]
    assert top_item['title'] == '离散数学复习笔记'
    assert top_item['ai_score'] > 0
    assert top_item['ai_reason']
    assert '类别偏好匹配' in top_item['ai_tags']


def test_record_browse_history_requires_login_and_persists_valid_products(client, db_session):
    seller = create_user(
        db_session,
        student_no='2023007006',
        email='recommend-seller-3@test.com',
        phone='13800007006',
    )
    current_user = create_user(
        db_session,
        student_no='2023007007',
        email='recommend-browser@test.com',
        phone='13800007007',
    )
    category = create_category(db_session)
    first_product = create_product(db_session, seller.user_id, category.category_id, title='高等数学辅导书')
    second_product = create_product(db_session, seller.user_id, category.category_id, title='线性代数笔记')

    unauthorized_response = client.post(
        '/api/recommendations/browse-history',
        json={'product_ids': [first_product.product_id]},
    )
    assert unauthorized_response.status_code == 401

    headers = login_and_get_headers(client, current_user.student_no)
    response = client.post(
        '/api/recommendations/browse-history',
        headers=headers,
        json={'product_ids': [first_product.product_id, second_product.product_id, first_product.product_id]},
    )

    assert response.status_code == 201
    assert response.json()['data']['recorded_count'] == 2
    records = db_session.query(BrowseHistory).filter_by(user_id=current_user.user_id).all()
    assert len(records) == 2
    assert {record.product_id for record in records} == {first_product.product_id, second_product.product_id}
