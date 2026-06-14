from decimal import Decimal

from app.core.security import hash_password
from app.models.product import Category, Product
from app.models.review import Review
from app.models.user import User


def create_user(db_session, **overrides):
    payload = {
        'student_no': '2023004001',
        'user_name': '评价买家',
        'gender': '女',
        'phone': '13800000051',
        'email': 'review-buyer@test.com',
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
        'category_name': '数码产品',
        'description': '数码类商品',
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
        'title': '评价测试商品',
        'description': '用于评价接口测试',
        'price': Decimal('88.00'),
        'category_id': category.category_id,
        'trade_location': '一食堂门口',
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


def create_completed_order(client, buyer_headers, seller_headers, product_id):
    create_response = client.post('/api/orders', headers=buyer_headers, json={'product_id': product_id})
    order_id = create_response.json()['data']['order_id']
    client.patch(f'/api/orders/{order_id}/confirm', headers=seller_headers)
    client.patch(f'/api/orders/{order_id}/complete', headers=buyer_headers)
    return order_id


def test_create_review_success(client, db_session):
    seller = create_user(
        db_session,
        student_no='2023004002',
        user_name='评价卖家',
        phone='13800000052',
        email='review-seller@test.com',
        credit_score=100,
    )
    buyer = create_user(db_session)
    product = create_product(db_session, seller.user_id)
    buyer_headers = login_and_get_headers(client, buyer.student_no)
    seller_headers = login_and_get_headers(client, seller.student_no)
    order_id = create_completed_order(client, buyer_headers, seller_headers, product.product_id)

    response = client.post(
        '/api/reviews',
        headers=buyer_headers,
        json={'order_id': order_id, 'score': 5, 'content': '卖家沟通顺畅，商品与描述一致。'},
    )

    assert response.status_code == 201
    assert response.json()['data']['order_id'] == order_id
    assert response.json()['data']['reviewer_name'] == buyer.user_name
    assert response.json()['data']['reviewed_user_name'] == seller.user_name
    db_session.refresh(seller)
    assert seller.credit_score == 102

    list_response = client.get(f'/api/reviews/order/{order_id}')
    assert list_response.status_code == 200
    assert list_response.json()['data'][0]['reviewer_name'] == buyer.user_name
    assert list_response.json()['data'][0]['reviewed_user_name'] == seller.user_name


def test_reject_review_for_incomplete_order(client, db_session):
    seller = create_user(
        db_session,
        student_no='2023004003',
        user_name='未完成卖家',
        phone='13800000053',
        email='review-incomplete-seller@test.com',
    )
    buyer = create_user(
        db_session,
        student_no='2023004004',
        user_name='未完成买家',
        phone='13800000054',
        email='review-incomplete-buyer@test.com',
    )
    product = create_product(db_session, seller.user_id)
    buyer_headers = login_and_get_headers(client, buyer.student_no)
    order_id = client.post('/api/orders', headers=buyer_headers, json={'product_id': product.product_id}).json()['data']['order_id']

    response = client.post(
        '/api/reviews',
        headers=buyer_headers,
        json={'order_id': order_id, 'score': 4, 'content': '先试着评价一下'},
    )

    assert response.status_code == 400
    assert response.json()['detail'] == '只有已完成订单才可以评价'


def test_reject_duplicate_review(client, db_session):
    seller = create_user(
        db_session,
        student_no='2023004005',
        user_name='重复卖家',
        phone='13800000055',
        email='review-repeat-seller@test.com',
    )
    buyer = create_user(
        db_session,
        student_no='2023004006',
        user_name='重复买家',
        phone='13800000056',
        email='review-repeat-buyer@test.com',
    )
    product = create_product(db_session, seller.user_id)
    buyer_headers = login_and_get_headers(client, buyer.student_no)
    seller_headers = login_and_get_headers(client, seller.student_no)
    order_id = create_completed_order(client, buyer_headers, seller_headers, product.product_id)

    first_response = client.post(
        '/api/reviews',
        headers=buyer_headers,
        json={'order_id': order_id, 'score': 5, 'content': '第一次评价'},
    )
    assert first_response.status_code == 201

    second_response = client.post(
        '/api/reviews',
        headers=buyer_headers,
        json={'order_id': order_id, 'score': 4, 'content': '重复提交评价'},
    )

    assert second_response.status_code == 400
    assert second_response.json()['detail'] == '该订单已经评价过了'

    reviews = db_session.query(Review).all()
    assert len(reviews) == 1
