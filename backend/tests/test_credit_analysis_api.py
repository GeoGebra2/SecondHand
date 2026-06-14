from decimal import Decimal

from app.core.security import hash_password
from app.models.order_info import OrderInfo
from app.models.product import Product
from app.models.review import Review
from app.models.user import User
from app.models.user_report import UserReport


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


def create_report(db_session, reporter, reported_user, reason='虚假交易'):
    report = UserReport(
        reporter_id=reporter.user_id,
        reported_user_id=reported_user.user_id,
        reason=reason,
        description='测试举报记录',
        status='PENDING',
    )
    db_session.add(report)
    db_session.commit()
    db_session.refresh(report)
    return report


def login_and_get_headers(client, account, password='student123'):
    response = client.post('/api/auth/login', json={'account': account, 'password': password})
    token = response.json()['data']['access_token']
    return {'Authorization': f'Bearer {token}'}


def test_credit_analysis_uses_role_specific_metrics(client, db_session):
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
        user_name='低分被举报卖家',
        phone='13800007002',
        email='risky-seller@test.com',
    )
    cancelling_buyer = create_user(
        db_session,
        student_no='2023007003',
        user_name='高责任取消率买家',
        phone='13800007003',
        email='risky-buyer@test.com',
    )
    reporter = create_user(
        db_session,
        student_no='2023007004',
        user_name='举报人',
        phone='13800007004',
        email='reporter@test.com',
    )
    product = create_product(db_session, risky_seller.user_id)

    for _ in range(3):
        create_order(db_session, product, cancelling_buyer, risky_seller, 'CANCELLED', cancelling_buyer.user_id)
    completed_orders = [
        create_order(db_session, product, cancelling_buyer, risky_seller, 'COMPLETED')
        for _ in range(2)
    ]
    create_order(db_session, product, cancelling_buyer, risky_seller, 'CANCELLED')
    for order in completed_orders:
        db_session.add(
            Review(
                order_id=order.order_id,
                reviewer_id=cancelling_buyer.user_id,
                reviewed_user_id=risky_seller.user_id,
                score=2,
                content='体验较差',
            )
        )
    create_report(db_session, reporter, risky_seller)
    create_report(db_session, cancelling_buyer, risky_seller, reason='描述不符')
    db_session.commit()
    headers = login_and_get_headers(client, admin.student_no)

    response = client.get('/api/admin/credit-analysis', headers=headers)

    assert response.status_code == 200
    analyses = response.json()['data']
    seller_analysis = next(item for item in analyses if item['user_id'] == risky_seller.user_id)
    buyer_analysis = next(item for item in analyses if item['user_id'] == cancelling_buyer.user_id)

    assert seller_analysis['is_suspicious'] is True
    assert '卖家订单评分偏低' in seller_analysis['warning_reasons']
    assert '被举报次数较多' in seller_analysis['warning_reasons']
    assert '已接单后主动取消率偏高' not in seller_analysis['warning_reasons']
    assert seller_analysis['metrics']['seller_review_count'] == 2
    assert seller_analysis['metrics']['average_seller_review_score'] == 2
    assert seller_analysis['metrics']['report_count'] == 2
    assert seller_analysis['metrics']['responsible_cancelled_orders'] == 0

    assert buyer_analysis['is_suspicious'] is True
    assert '已接单后主动取消率偏高' in buyer_analysis['warning_reasons']
    assert '卖家订单评分偏低' not in buyer_analysis['warning_reasons']
    assert buyer_analysis['metrics']['accountable_order_count'] == 5
    assert buyer_analysis['metrics']['responsible_cancelled_orders'] == 3
    assert buyer_analysis['metrics']['responsible_cancellation_rate'] == 0.6
    assert buyer_analysis['metrics']['seller_review_count'] == 0
    assert buyer_analysis['metrics']['average_seller_review_score'] is None


def test_user_report_and_admin_block_flow(client, db_session):
    admin = create_user(
        db_session,
        student_no='2023007010',
        user_name='举报管理员',
        phone='13800007010',
        email='report-admin@test.com',
        role='admin',
    )
    reporter = create_user(
        db_session,
        student_no='2023007011',
        user_name='举报学生',
        phone='13800007011',
        email='reporter-flow@test.com',
    )
    reported_user = create_user(
        db_session,
        student_no='2023007012',
        user_name='被举报用户',
        phone='13800007012',
        email='reported@test.com',
    )
    product = create_product(db_session, reported_user.user_id)
    reporter_headers = login_and_get_headers(client, reporter.student_no)
    admin_headers = login_and_get_headers(client, admin.student_no)

    report_response = client.post(
        '/api/reports/users',
        headers=reporter_headers,
        json={
            'reported_user_id': reported_user.user_id,
            'reason': '虚假交易',
            'description': '商品信息和沟通内容不一致',
        },
    )
    self_report_response = client.post(
        '/api/reports/users',
        headers=reporter_headers,
        json={'reported_user_id': reporter.user_id, 'reason': '测试自举报'},
    )
    reports_response = client.get('/api/admin/reports', headers=admin_headers)
    block_response = client.patch(f'/api/admin/users/{reported_user.user_id}/block', headers=admin_headers)
    order_response = client.post(
        '/api/orders',
        headers=reporter_headers,
        json={'product_id': product.product_id, 'buyer_note': '想购买'},
    )
    unblock_response = client.patch(f'/api/admin/users/{reported_user.user_id}/unblock', headers=admin_headers)

    assert report_response.status_code == 201
    assert report_response.json()['data']['reported_user_id'] == reported_user.user_id
    assert self_report_response.status_code == 400
    assert self_report_response.json()['detail'] == '不能举报自己'

    assert reports_response.status_code == 200
    reports = reports_response.json()['data']
    assert len(reports) == 1
    assert reports[0]['reporter_id'] == reporter.user_id
    assert reports[0]['reported_user_id'] == reported_user.user_id

    assert block_response.status_code == 200
    assert block_response.json()['data']['status'] == 'blocked'
    assert order_response.status_code == 400
    assert order_response.json()['detail'] == '卖家当前不可交易'

    assert unblock_response.status_code == 200
    assert unblock_response.json()['data']['status'] == 'active'


def test_seller_risk_profile_endpoint_returns_warning_data(client, db_session):
    buyer = create_user(
        db_session,
        student_no='2023007020',
        user_name='画像查询买家',
        phone='13800007020',
        email='profile-buyer@test.com',
    )
    seller = create_user(
        db_session,
        student_no='2023007021',
        user_name='画像卖家',
        phone='13800007021',
        email='profile-seller@test.com',
    )
    reporter = create_user(
        db_session,
        student_no='2023007022',
        user_name='画像举报人',
        phone='13800007022',
        email='profile-reporter@test.com',
    )
    create_report(db_session, buyer, seller)
    create_report(db_session, reporter, seller, reason='异常账号')
    headers = login_and_get_headers(client, buyer.student_no)

    response = client.get(f'/api/products/sellers/{seller.user_id}/risk-profile', headers=headers)

    assert response.status_code == 200
    profile = response.json()['data']
    assert profile['user_id'] == seller.user_id
    assert profile['report_count'] == 2
    assert '被举报次数较多' in profile['warning_reasons']
    assert profile['risk_level'] in {'MEDIUM', 'HIGH'}


def test_credit_analysis_requires_admin(client, db_session):
    student = create_user(db_session)
    headers = login_and_get_headers(client, student.student_no)

    response = client.get('/api/admin/credit-analysis', headers=headers)

    assert response.status_code == 403
    assert response.json()['detail'] == '无管理员权限'
