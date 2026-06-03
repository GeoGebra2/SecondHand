from decimal import Decimal

from app.core.security import hash_password
from app.models.product import Category, Product, ProductImage
from app.models.user import User


def create_user(db_session, **overrides):
    payload = {
        'student_no': '2023005001',
        'user_name': '商品卖家',
        'gender': '女',
        'phone': '13800005001',
        'email': 'product-seller@test.com',
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


def create_product(db_session, seller_id, **overrides):
    payload = {
        'seller_id': seller_id,
        'title': '数据库教材',
        'description': '配套期末复习笔记',
        'price': Decimal('35.00'),
        'category_name': '教材资料',
        'trade_location': '图书馆门口',
        'status': 'ON_SALE',
    }
    payload.update(overrides)
    product = Product(**payload)
    db_session.add(product)
    db_session.commit()
    db_session.refresh(product)
    return product


def login_and_get_headers(client, account, password='student123'):
    response = client.post('/api/auth/login', json={'account': account, 'password': password})
    token = response.json()['data']['access_token']
    return {'Authorization': f'Bearer {token}'}


def test_list_products_supports_search_filter_price_sort_and_images(client, db_session):
    seller = create_user(db_session)
    create_category(db_session)
    matched = create_product(db_session, seller.user_id)
    create_product(
        db_session,
        seller.user_id,
        title='蓝牙耳机',
        description='降噪耳机',
        price=Decimal('120.00'),
        category_name='数码产品',
    )
    db_session.add(ProductImage(product_id=matched.product_id, image_url='https://example.com/book.jpg', sort_order=0))
    db_session.commit()

    response = client.get(
        '/api/products',
        params={
            'keyword': '复习',
            'category_name': '教材资料',
            'min_price': '20',
            'max_price': '50',
            'sort_by': 'price',
            'sort_order': 'asc',
        },
    )

    assert response.status_code == 200
    data = response.json()['data']
    assert len(data) == 1
    assert data[0]['title'] == '数据库教材'
    assert data[0]['image_urls'] == ['https://example.com/book.jpg']


def test_create_product_persists_category_and_images(client, db_session):
    seller = create_user(db_session)
    headers = login_and_get_headers(client, seller.student_no)

    response = client.post(
        '/api/products',
        headers=headers,
        json={
            'title': '九成新台灯',
            'description': '亮度可调，适合宿舍学习',
            'price': '45.00',
            'category_name': '生活用品',
            'trade_location': '宿舍楼下',
            'image_urls': ['https://example.com/lamp-1.jpg', 'https://example.com/lamp-2.jpg'],
        },
    )

    assert response.status_code == 201
    data = response.json()['data']
    assert data['category_name'] == '生活用品'
    assert data['image_urls'] == ['https://example.com/lamp-1.jpg', 'https://example.com/lamp-2.jpg']
    assert db_session.query(Category).filter_by(category_name='生活用品').count() == 1


def test_seller_can_update_and_offline_own_product(client, db_session):
    seller = create_user(db_session)
    create_category(db_session)
    product = create_product(db_session, seller.user_id)
    headers = login_and_get_headers(client, seller.student_no)

    update_response = client.put(
        f'/api/products/{product.product_id}',
        headers=headers,
        json={
            'title': '数据库教材第二版',
            'description': '补充课堂笔记',
            'price': '40.00',
            'category_name': '教材资料',
            'trade_location': '教学楼 A 区',
            'image_urls': ['https://example.com/db-book.jpg'],
        },
    )
    offline_response = client.patch(f'/api/products/{product.product_id}/offline', headers=headers)

    assert update_response.status_code == 200
    assert update_response.json()['data']['title'] == '数据库教材第二版'
    assert offline_response.status_code == 200
    assert offline_response.json()['data']['status'] == 'OFFLINE'


def test_rejects_managing_other_seller_product(client, db_session):
    seller = create_user(db_session)
    other = create_user(
        db_session,
        student_no='2023005002',
        email='other-seller@test.com',
        phone='13800005002',
    )
    create_category(db_session)
    product = create_product(db_session, seller.user_id)
    headers = login_and_get_headers(client, other.student_no)

    response = client.patch(f'/api/products/{product.product_id}/offline', headers=headers)

    assert response.status_code == 403
    assert response.json()['detail'] == '只能管理自己发布的商品'


def test_create_and_update_category(client, db_session):
    manager = create_user(db_session)
    headers = login_and_get_headers(client, manager.student_no)

    create_response = client.post(
        '/api/products/categories',
        headers=headers,
        json={'category_name': '运动户外', 'description': '运动装备', 'sort_order': 3},
    )
    category_id = create_response.json()['data']['category_id']
    update_response = client.put(
        f'/api/products/categories/{category_id}',
        headers=headers,
        json={
            'category_name': '运动健身',
            'description': '运动和健身用品',
            'sort_order': 4,
            'status': 'ACTIVE',
        },
    )

    assert create_response.status_code == 201
    assert update_response.status_code == 200
    assert update_response.json()['data']['category_name'] == '运动健身'


def test_update_category_name_syncs_existing_products(client, db_session):
    seller = create_user(db_session)
    category = create_category(db_session)
    product = create_product(db_session, seller.user_id, category_name=category.category_name)
    headers = login_and_get_headers(client, seller.student_no)

    response = client.put(
        f'/api/products/categories/{category.category_id}',
        headers=headers,
        json={
            'category_name': '课程资料',
            'description': '教材和课堂资料',
            'sort_order': 2,
            'status': 'ACTIVE',
        },
    )

    assert response.status_code == 200
    db_session.refresh(product)
    assert product.category_name == '课程资料'


def test_rejects_blank_product_title_after_strip(client, db_session):
    seller = create_user(db_session)
    headers = login_and_get_headers(client, seller.student_no)

    response = client.post(
        '/api/products',
        headers=headers,
        json={
            'title': '   ',
            'description': '空白标题测试',
            'price': '20.00',
            'category_name': '教材资料',
            'trade_location': '图书馆门口',
            'image_urls': [],
        },
    )

    assert response.status_code == 422
