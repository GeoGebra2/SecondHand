from decimal import Decimal

from app.core.security import hash_password
from app.models.product import Category, Product
from app.models.user import User


def create_user(db_session, **overrides):
    payload = {
        'student_no': '2023006001',
        'user_name': '社交测试用户',
        'gender': '男',
        'phone': '13800006001',
        'email': 'social-user@test.com',
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
        'category_name': '生活用品',
        'description': '生活日用',
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
        'title': '保温杯',
        'description': '九成新',
        'price': Decimal('20.00'),
        'trade_location': '宿舍楼下',
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


def test_create_and_list_favorites(client, db_session):
    seller = create_user(db_session, student_no='2023006002', email='social-seller@test.com', phone='13800006002')
    buyer = create_user(db_session)
    category = create_category(db_session)
    product = create_product(db_session, seller.user_id, category.category_id)
    headers = login_and_get_headers(client, buyer.student_no)

    create_response = client.post('/api/favorites', headers=headers, json={'product_id': product.product_id})
    list_response = client.get('/api/favorites', headers=headers)

    assert create_response.status_code == 201
    assert list_response.status_code == 200
    assert list_response.json()['data'][0]['product_title'] == '保温杯'


def test_create_notification_and_list_for_receiver(client, db_session):
    sender = create_user(db_session)
    receiver = create_user(
        db_session,
        student_no='2023006003',
        email='social-receiver@test.com',
        phone='13800006003',
    )
    sender_headers = login_and_get_headers(client, sender.student_no)
    receiver_headers = login_and_get_headers(client, receiver.student_no)

    create_response = client.post(
        '/api/notifications',
        headers=sender_headers,
        json={'receiver_id': receiver.user_id, 'content': '请及时处理你的订单'},
    )
    list_response = client.get('/api/notifications', headers=receiver_headers)

    assert create_response.status_code == 201
    assert list_response.status_code == 200
    assert list_response.json()['data'][0]['content'] == '请及时处理你的订单'


def test_remove_favorite(client, db_session):
    seller = create_user(db_session, student_no='2023006004', email='social-seller2@test.com', phone='13800006004')
    buyer = create_user(db_session)
    category = create_category(db_session)
    product = create_product(db_session, seller.user_id, category.category_id)
    headers = login_and_get_headers(client, buyer.student_no)

    create_response = client.post('/api/favorites', headers=headers, json={'product_id': product.product_id})
    assert create_response.status_code == 201

    delete_response = client.delete(f'/api/favorites/{product.product_id}', headers=headers)
    assert delete_response.status_code == 200

    list_response = client.get('/api/favorites', headers=headers)
    assert list_response.status_code == 200
    assert list_response.json()['data'] == []


def test_create_order_sends_notification_to_seller(client, db_session):
    seller = create_user(db_session, student_no='2023006005', email='notify-seller@test.com', phone='13800006005')
    buyer = create_user(db_session)
    category = create_category(db_session)
    product = create_product(db_session, seller.user_id, category.category_id)

    buyer_headers = login_and_get_headers(client, buyer.student_no)
    seller_headers = login_and_get_headers(client, seller.student_no)

    create_response = client.post('/api/orders', headers=buyer_headers, json={'product_id': product.product_id})
    assert create_response.status_code == 201

    # seller should receive a notification
    list_response = client.get('/api/notifications', headers=seller_headers)
    assert list_response.status_code == 200
    assert len(list_response.json()['data']) >= 1
    contents = [n['content'] for n in list_response.json()['data']]
    assert any('您的商品' in c and '有新的订单' in c for c in contents)
