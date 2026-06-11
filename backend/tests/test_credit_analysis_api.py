from decimal import Decimal

from app.core.security import hash_password
from app.models.order_info import OrderInfo
from app.models.product import Product
from app.models.review import Review
from app.models.user import User


def create_user(db_session, **overrides):
    payload = {
        'student_no': '2023007001',
        'user_name': '信用测试用户',
        'gender': '男',
        'phone': '13800007001',
        'email': 'credit-user@test.com',
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


def create_product(db_session, seller_id, **overrides):
    payload = {
        'seller_id': seller_id,
        'title': '信用测试商品',
        'description': '用于信用分析测试',
        'price': Decimal('30.00'),
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


def create_order(db_session, product, buyer, seller, status):
    order = OrderInfo(
        product_id=product.product_id,
        buyer_id=buyer.user_id,
        seller_id=seller.user_id,
        order_amount=product.price,
        order_status=status,
        trade_method='offline',
        trade_location=product.trade_location,
    )
    db_session.add(order)
    db_session.commit()
    db_session.refresh(order)
    return order


def login_and_get_headers(client, account, password='student123'):
    response = client.post('/api/auth/login', json={'account': account, 'password': password})
    token = response.json()['data']['access_token']
    return {'Authorization': f'Bearer {token}'}


def test_admin_can_get_credit_analysis_and_flags_suspicious_user(client, db_session):
    admin = create_user(
        db_session,
        student_no='2023007000',
        user_name='信用管理员',
        phone='13800007000',
        email='credit-admin@test.com',
        role='admin',
    )
    risky_seller = create_user(
        db_session,
        student_no='2023007002',
        user_name='高风险卖家',
        phone='13800007002',
        email='risky-seller@test.com',
    )
    buyer = create_user(
        db_session,
        student_no='2023007003',
        user_name='信用买家',
        phone='13800007003',
        email='credit-buyer@test.com',
    )
    product = create_product(db_session, risky_seller.user_id)
    cancelled_orders = [
        create_order(db_session, product, buyer, risky_seller, 'CANCELLED')
        for _ in range(3)
    ]
    completed_order = create_order(db_session, product, buyer, risky_seller, 'COMPLETED')
    db_session.add(
        Review(
            order_id=completed_order.order_id,
            reviewer_id=buyer.user_id,
            reviewed_user_id=risky_seller.user_id,
            score=2,
            content='多次取消且体验较差',
        )
    )
    db_session.commit()
    headers = login_and_get_headers(client, admin.student_no)

    response = client.get('/api/admin/credit-analysis', headers=headers)

    assert response.status_code == 200
    analyses = response.json()['data']
    risky_analysis = next(item for item in analyses if item['user_id'] == risky_seller.user_id)
    assert risky_analysis['is_suspicious'] is True
    assert risky_analysis['risk_level'] in {'MEDIUM', 'HIGH'}
    assert '订单取消率偏高' in risky_analysis['warning_reasons']
    assert risky_analysis['metrics']['cancelled_orders'] == len(cancelled_orders)


def test_credit_analysis_requires_admin(client, db_session):
    student = create_user(db_session)
    headers = login_and_get_headers(client, student.student_no)

    response = client.get('/api/admin/credit-analysis', headers=headers)

    assert response.status_code == 403
    assert response.json()['detail'] == '无管理员权限'
