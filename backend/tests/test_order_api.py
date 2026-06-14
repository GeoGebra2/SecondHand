from decimal import Decimal

from app.core.security import hash_password
from app.models.notification import Notification
from app.models.order_info import OrderInfo
from app.models.product import Category, Product
from app.models.user import User


def create_user(db_session, **overrides):
    payload = {
        'student_no': '2023003001',
        'user_name': '买家同学',
        'gender': '男',
        'phone': '13800000031',
        'email': 'buyer@test.com',
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
    category = create_category(db_session)
    payload = {
        'seller_id': seller_id,
        'title': '测试商品',
        'description': '用于订单接口测试',
        'price': Decimal('66.00'),
        'category_id': category.category_id,
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


def test_create_order_success(client, db_session):
    seller = create_user(
        db_session,
        student_no='2023003002',
        user_name='卖家同学',
        phone='13800000032',
        email='seller@test.com',
    )
    buyer = create_user(db_session)
    product = create_product(db_session, seller.user_id)
    headers = login_and_get_headers(client, buyer.student_no)

    response = client.post(
        '/api/orders',
        headers=headers,
        json={'product_id': product.product_id, 'buyer_note': '晚上自提'},
    )

    assert response.status_code == 201
    body = response.json()
    assert body['data']['order_status'] == 'PENDING'
    db_session.refresh(product)
    assert product.status == 'LOCKED'
    notification = db_session.query(Notification).filter_by(receiver_id=seller.user_id).one()
    assert '下单' in notification.content
    assert product.title in notification.content


def test_create_order_rejects_self_purchase(client, db_session):
    seller = create_user(db_session, student_no='2023003009', email='self@test.com', phone='13800000039')
    product = create_product(db_session, seller.user_id)
    headers = login_and_get_headers(client, seller.student_no)

    response = client.post('/api/orders', headers=headers, json={'product_id': product.product_id})

    assert response.status_code == 400
    assert response.json()['detail'] == '不能购买自己发布的商品'


def test_seller_can_confirm_order(client, db_session):
    seller = create_user(
        db_session,
        student_no='2023003003',
        user_name='卖家确认用户',
        phone='13800000033',
        email='seller-confirm@test.com',
    )
    buyer = create_user(db_session, student_no='2023003004', email='buyer-confirm@test.com', phone='13800000034')
    product = create_product(db_session, seller.user_id)
    buyer_headers = login_and_get_headers(client, buyer.student_no)
    create_response = client.post('/api/orders', headers=buyer_headers, json={'product_id': product.product_id})
    order_id = create_response.json()['data']['order_id']
    seller_headers = login_and_get_headers(client, seller.student_no)

    response = client.patch(f'/api/orders/{order_id}/confirm', headers=seller_headers)

    assert response.status_code == 200
    assert response.json()['data']['order_status'] == 'IN_PROGRESS'


def test_buyer_can_complete_order(client, db_session):
    seller = create_user(
        db_session,
        student_no='2023003005',
        user_name='卖家完成用户',
        phone='13800000035',
        email='seller-complete@test.com',
    )
    buyer = create_user(db_session, student_no='2023003006', email='buyer-complete@test.com', phone='13800000036')
    product = create_product(db_session, seller.user_id)
    buyer_headers = login_and_get_headers(client, buyer.student_no)
    order_id = client.post('/api/orders', headers=buyer_headers, json={'product_id': product.product_id}).json()['data']['order_id']
    seller_headers = login_and_get_headers(client, seller.student_no)
    client.patch(f'/api/orders/{order_id}/confirm', headers=seller_headers)

    response = client.patch(f'/api/orders/{order_id}/complete', headers=buyer_headers)

    assert response.status_code == 200
    assert response.json()['data']['order_status'] == 'COMPLETED'
    db_session.refresh(product)
    assert product.status == 'SOLD'


def test_rejects_invalid_status_transition(client, db_session):
    seller = create_user(
        db_session,
        student_no='2023003007',
        user_name='卖家状态用户',
        phone='13800000037',
        email='seller-status@test.com',
    )
    buyer = create_user(db_session, student_no='2023003008', email='buyer-status@test.com', phone='13800000038')
    product = create_product(db_session, seller.user_id)
    buyer_headers = login_and_get_headers(client, buyer.student_no)
    order_id = client.post('/api/orders', headers=buyer_headers, json={'product_id': product.product_id}).json()['data']['order_id']

    response = client.patch(f'/api/orders/{order_id}/complete', headers=buyer_headers)

    assert response.status_code == 400
    assert response.json()['detail'] == '当前订单状态无法完成'


def test_cancel_order_restores_product_status(client, db_session):
    seller = create_user(
        db_session,
        student_no='2023003010',
        user_name='卖家取消用户',
        phone='13800000040',
        email='seller-cancel@test.com',
    )
    buyer = create_user(db_session, student_no='2023003011', email='buyer-cancel@test.com', phone='13800000041')
    product = create_product(db_session, seller.user_id)
    buyer_headers = login_and_get_headers(client, buyer.student_no)
    order_id = client.post('/api/orders', headers=buyer_headers, json={'product_id': product.product_id}).json()['data']['order_id']

    response = client.patch(
        f'/api/orders/{order_id}/cancel',
        headers=buyer_headers,
        json={'cancel_reason': '临时有事无法面交'},
    )

    assert response.status_code == 200
    assert response.json()['data']['order_status'] == 'CANCELLED'
    db_session.refresh(product)
    assert product.status == 'ON_SALE'

    order = db_session.get(OrderInfo, order_id)
    assert order.cancel_reason == '临时有事无法面交'
    assert order.cancel_user_id is None


def test_cancel_after_confirm_records_responsible_user(client, db_session):
    seller = create_user(
        db_session,
        student_no='2023003012',
        user_name='接单后取消卖家',
        phone='13800000042',
        email='seller-cancel-after-confirm@test.com',
    )
    buyer = create_user(db_session, student_no='2023003013', email='buyer-cancel-after-confirm@test.com', phone='13800000043')
    product = create_product(db_session, seller.user_id)
    buyer_headers = login_and_get_headers(client, buyer.student_no)
    seller_headers = login_and_get_headers(client, seller.student_no)
    order_id = client.post('/api/orders', headers=buyer_headers, json={'product_id': product.product_id}).json()['data']['order_id']
    client.patch(f'/api/orders/{order_id}/confirm', headers=seller_headers)

    response = client.patch(
        f'/api/orders/{order_id}/cancel',
        headers=seller_headers,
        json={'cancel_reason': '卖家无法继续交易'},
    )

    assert response.status_code == 200
    assert response.json()['data']['order_status'] == 'CANCELLED'
    order = db_session.get(OrderInfo, order_id)
    assert order.cancel_user_id == seller.user_id
