from decimal import Decimal

from app.core.security import hash_password
from app.models.order_info import OrderInfo
from app.models.product import Category, Product
from app.models.review import Review
from app.models.user import User


def create_user(db_session, **overrides):
    payload = {
        'student_no': '2023090001',
        'user_name': '信用测试用户',
        'gender': '男',
        'phone': '13800009001',
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


def create_category(db_session, **overrides):
    payload = {
        'category_name': '信用测试分类',
        'description': '信用测试',
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
        'title': '信用测试商品',
        'description': '用于信用测试',
        'price': Decimal('66.00'),
        'category_id': category_id,
        'trade_location': '图书馆门口',
        'status': 'ON_SALE',
    }
    payload.update(overrides)
    product = Product(**payload)
    db_session.add(product)
    db_session.commit()
    db_session.refresh(product)
    return product


def create_order(db_session, product, buyer, seller, status, cancel_user_id=None):
    order = OrderInfo(
        product_id=product.product_id,
        buyer_id=buyer.user_id,
        seller_id=seller.user_id,
        order_amount=product.price,
        order_status=status,
        trade_method='offline',
        trade_location=product.trade_location,
        cancel_user_id=cancel_user_id,
    )
    db_session.add(order)
    db_session.commit()
    db_session.refresh(order)
    return order


def login_and_get_headers(client, account, password='student123'):
    response = client.post('/api/auth/login', json={'account': account, 'password': password})
    token = response.json()['data']['access_token']
    return {'Authorization': f'Bearer {token}'}


def test_credit_report_and_admin_block_flow(client, db_session):
    admin = create_user(
        db_session,
        student_no='2023090000',
        user_name='信用管理员',
        phone='13800009000',
        email='credit-admin@test.com',
        role='admin',
    )
    seller = create_user(
        db_session,
        student_no='2023090002',
        user_name='低分卖家',
        phone='13800009002',
        email='credit-seller@test.com',
    )
    buyer = create_user(
        db_session,
        student_no='2023090003',
        user_name='责任取消买家',
        phone='13800009003',
        email='credit-buyer@test.com',
    )
    reporter = create_user(
        db_session,
        student_no='2023090004',
        user_name='举报人',
        phone='13800009004',
        email='credit-reporter@test.com',
    )
    category = create_category(db_session)
    product = create_product(db_session, seller.user_id, category.category_id)

    for _ in range(3):
        create_order(db_session, product, buyer, seller, 'CANCELLED', buyer.user_id)
    completed_orders = [create_order(db_session, product, buyer, seller, 'COMPLETED') for _ in range(2)]
    create_order(db_session, product, buyer, seller, 'CANCELLED')
    for order in completed_orders:
        db_session.add(
            Review(
                order_id=order.order_id,
                reviewer_id=buyer.user_id,
                reviewed_user_id=seller.user_id,
                score=2,
                content='体验较差',
            )
        )
    db_session.commit()

    buyer_headers = login_and_get_headers(client, buyer.student_no)
    reporter_headers = login_and_get_headers(client, reporter.student_no)
    admin_headers = login_and_get_headers(client, admin.student_no)

    report_response = client.post(
        '/api/reports/users',
        headers=buyer_headers,
        json={'reported_user_id': seller.user_id, 'reason': '虚假交易'},
    )
    second_report_response = client.post(
        '/api/reports/users',
        headers=reporter_headers,
        json={'reported_user_id': seller.user_id, 'reason': '描述不符'},
    )
    analysis_response = client.get('/api/admin/credit-analysis', headers=admin_headers)
    reports_response = client.get('/api/admin/reports', headers=admin_headers)
    risk_response = client.get(f'/api/products/sellers/{seller.user_id}/risk-profile', headers=buyer_headers)
    block_response = client.patch(f'/api/admin/users/{seller.user_id}/block', headers=admin_headers)

    assert report_response.status_code == 201
    assert second_report_response.status_code == 201
    assert reports_response.status_code == 200
    assert len(reports_response.json()['data']) == 2

    assert analysis_response.status_code == 200
    analyses = analysis_response.json()['data']
    seller_analysis = next(item for item in analyses if item['user_id'] == seller.user_id)
    buyer_analysis = next(item for item in analyses if item['user_id'] == buyer.user_id)
    assert '卖家订单评分偏低' in seller_analysis['warning_reasons']
    assert '被举报次数较多' in seller_analysis['warning_reasons']
    assert '已接单后主动取消率偏高' not in seller_analysis['warning_reasons']
    assert buyer_analysis['metrics']['responsible_cancelled_orders'] == 3
    assert buyer_analysis['metrics']['responsible_cancellation_rate'] == 0.6

    assert risk_response.status_code == 200
    assert risk_response.json()['data']['report_count'] == 2
    assert block_response.status_code == 200
    assert block_response.json()['data']['status'] == 'blocked'
