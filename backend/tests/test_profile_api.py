from app.core.security import hash_password
from app.models.notification import Notification
from app.models.user import User


def create_user(db_session, **overrides):
    payload = {
        'student_no': '2023002001',
        'user_name': '资料测试用户',
        'gender': '女',
        'phone': '13800000008',
        'email': 'profile@test.com',
        'password_hash': hash_password('student123'),
        'role': 'student',
        'credit_score': 98,
        'status': 'active',
        'verify_status': 'verified',
    }
    payload.update(overrides)
    user = User(**payload)
    db_session.add(user)
    db_session.commit()
    db_session.refresh(user)
    return user


def login_and_get_headers(client, account='2023002001', password='student123'):
    response = client.post(
        '/api/auth/login',
        json={'account': account, 'password': password},
    )
    token = response.json()['data']['access_token']
    return {'Authorization': f'Bearer {token}'}


def test_get_current_user_profile(client, db_session):
    create_user(db_session)
    headers = login_and_get_headers(client)

    response = client.get('/api/auth/me', headers=headers)

    assert response.status_code == 200
    body = response.json()
    assert body['data']['student_no'] == '2023002001'
    assert body['data']['user_name'] == '资料测试用户'
    assert body['data']['credit_score'] == 80


def test_get_account_status_returns_computed_credit_and_notifications(client, db_session):
    user = create_user(db_session)
    db_session.add(
        Notification(
            receiver_id=user.user_id,
            content='测试站内通知',
        )
    )
    db_session.commit()
    headers = login_and_get_headers(client)

    response = client.get('/api/auth/me/status', headers=headers)

    assert response.status_code == 200
    data = response.json()['data']
    assert data['user']['user_id'] == user.user_id
    assert data['user']['credit_score'] == data['computed_score']
    assert data['computed_score'] == 80
    assert data['notifications'][0]['content'] == '测试站内通知'


def test_account_status_allows_blocked_user_to_receive_notice(client, db_session):
    user = create_user(db_session)
    headers = login_and_get_headers(client)
    user.status = 'blocked'
    db_session.add(
        Notification(
            receiver_id=user.user_id,
            content='你的账号已被管理员拉黑',
        )
    )
    db_session.add(user)
    db_session.commit()

    me_response = client.get('/api/auth/me', headers=headers)
    status_response = client.get('/api/auth/me/status', headers=headers)

    assert me_response.status_code == 401
    assert status_response.status_code == 200
    data = status_response.json()['data']
    assert data['user']['status'] == 'blocked'
    assert data['notifications'][0]['content'] == '你的账号已被管理员拉黑'


def test_update_profile_success(client, db_session):
    create_user(db_session)
    headers = login_and_get_headers(client)

    response = client.put(
        '/api/auth/me',
        headers=headers,
        json={
            'user_name': '新昵称',
            'phone': '13900001111',
            'email': 'updated@test.com',
            'gender': '男',
            'bio': '更新后的个人简介',
        },
    )

    assert response.status_code == 200
    body = response.json()
    assert body['data']['user_name'] == '新昵称'
    assert body['data']['email'] == 'updated@test.com'
    assert body['data']['bio'] == '更新后的个人简介'


def test_get_profile_requires_login(client):
    response = client.get('/api/auth/me')

    assert response.status_code == 401
    assert response.json()['detail'] == '请先登录'


def test_update_profile_rejects_duplicate_email(client, db_session):
    create_user(db_session)
    create_user(
        db_session,
        student_no='2023002002',
        email='duplicate@test.com',
        phone='13800000018',
    )
    headers = login_and_get_headers(client)

    response = client.put(
        '/api/auth/me',
        headers=headers,
        json={'email': 'duplicate@test.com'},
    )

    assert response.status_code == 400
    assert response.json()['detail'] == '该邮箱已被其他用户使用'
