from app.core.security import hash_password
from app.models.user import User


def create_user(db_session, **overrides):
    payload = {
        'student_no': '2023001001',
        'user_name': '测试用户',
        'gender': '男',
        'phone': '13800000001',
        'email': 'user1@test.com',
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


def test_register_success(client):
    response = client.post(
        '/api/auth/register',
        json={
            'student_no': '2023123456',
            'user_name': '张三',
            'password': 'abc12345',
            'email': 'zhangsan@test.com',
            'phone': '13800000000',
            'gender': '男',
        },
    )

    assert response.status_code == 201
    body = response.json()
    assert body['message'] == '注册成功'
    assert body['data']['student_no'] == '2023123456'


def test_register_rejects_duplicate_student_no(client, db_session):
    create_user(db_session)

    response = client.post(
        '/api/auth/register',
        json={
            'student_no': '2023001001',
            'user_name': '李四',
            'password': 'abc12345',
            'email': 'lisi@test.com',
            'phone': '13800000009',
            'gender': '女',
        },
    )

    assert response.status_code == 400
    assert response.json()['detail'] == '该学号已注册'


def test_register_rejects_duplicate_email(client, db_session):
    create_user(db_session)

    response = client.post(
        '/api/auth/register',
        json={
            'student_no': '2023001002',
            'user_name': '李四',
            'password': 'abc12345',
            'email': 'user1@test.com',
            'phone': '13800000009',
            'gender': '女',
        },
    )

    assert response.status_code == 400
    assert response.json()['detail'] == '该邮箱已注册'


def test_register_rejects_short_password(client):
    response = client.post(
        '/api/auth/register',
        json={
            'student_no': '2023001002',
            'user_name': '李四',
            'password': '123',
            'email': 'short@test.com',
            'phone': '13800000009',
            'gender': '女',
        },
    )

    assert response.status_code == 422


def test_login_with_student_no_success(client, db_session):
    create_user(db_session)

    response = client.post(
        '/api/auth/login',
        json={'account': '2023001001', 'password': 'student123'},
    )

    assert response.status_code == 200
    body = response.json()
    assert body['message'] == '登录成功'
    assert body['data']['access_token']
    assert body['data']['user']['student_no'] == '2023001001'


def test_login_with_email_success(client, db_session):
    create_user(db_session)

    response = client.post(
        '/api/auth/login',
        json={'account': 'user1@test.com', 'password': 'student123'},
    )

    assert response.status_code == 200
    assert response.json()['data']['user']['email'] == 'user1@test.com'


def test_login_rejects_wrong_password(client, db_session):
    create_user(db_session)

    response = client.post(
        '/api/auth/login',
        json={'account': '2023001001', 'password': 'wrongpass1'},
    )

    assert response.status_code == 400
    assert response.json()['detail'] == '账号或密码错误'


def test_login_rejects_missing_user(client):
    response = client.post(
        '/api/auth/login',
        json={'account': 'notfound@test.com', 'password': 'student123'},
    )

    assert response.status_code == 400
    assert response.json()['detail'] == '账号或密码错误'
