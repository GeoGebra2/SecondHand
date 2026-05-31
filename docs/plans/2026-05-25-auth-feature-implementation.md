# Auth Feature Implementation Plan

> **For Claude:** REQUIRED SUB-SKILL: Use superpowers:executing-plans to implement this plan task-by-task.

**Goal:** 为校园二手交易平台实现“用户注册、登录、身份认证和个人信息维护”能力，采用方案 A：学号实名登记 + JWT 登录态 + 个人中心维护。

**Architecture:** 后端继续使用 FastAPI，新增数据库访问层、用户模型、认证服务、JWT 鉴权和资料维护接口；前端继续使用 Vue 3，新增登录页、注册页、个人中心页和路由守卫。身份认证采用“学号实名登记”简化方案，注册成功后即完成基础实名登记，同时保留 `verify_status` 字段以支持后续扩展为审核流。

**Tech Stack:** Vue 3, Vue Router, Axios, FastAPI, SQLAlchemy, PyMySQL, Passlib, Python-Jose, Pydantic

---

### Task 1: 扩展数据库与后端依赖

**Files:**
- Modify: `d:\数据库技术\大作业\SecondHand\backend\requirements.txt`
- Create: `d:\数据库技术\大作业\SecondHand\backend\app\db\base.py`
- Create: `d:\数据库技术\大作业\SecondHand\backend\app\db\session.py`
- Create: `d:\数据库技术\大作业\SecondHand\backend\app\models\user.py`
- Modify: `d:\数据库技术\大作业\SecondHand\backend\.env.example`

**Step 1: 增加依赖**

补充数据库和认证所需依赖：

```txt
sqlalchemy
pymysql
passlib[bcrypt]
python-jose[cryptography]
email-validator
```

**Step 2: 添加数据库配置**

在 `.env.example` 中加入：

```env
DATABASE_URL=mysql+pymysql://root:password@127.0.0.1:3306/secondhand
JWT_SECRET_KEY=change_me
JWT_ALGORITHM=HS256
JWT_EXPIRE_MINUTES=120
```

**Step 3: 创建用户表模型**

字段建议：

```python
user_id
student_no
user_name
gender
phone
email
password_hash
role
credit_score
status
verify_status
avatar_url
bio
create_time
update_time
last_login_time
```

**Step 4: 初始化数据库基类和会话**

为后续接口提供统一的 `SessionLocal` 和 `Base`。

**Step 5: 预期结果**

应用启动时已具备连接 MySQL 和映射 `user` 表的能力。

### Task 2: 设计认证与用户资料 Schema

**Files:**
- Create: `d:\数据库技术\大作业\SecondHand\backend\app\schemas\auth.py`
- Create: `d:\数据库技术\大作业\SecondHand\backend\app\schemas\user.py`
- Modify: `d:\数据库技术\大作业\SecondHand\backend\app\schemas\common.py`

**Step 1: 定义注册请求模型**

```python
class RegisterRequest(BaseModel):
    student_no: str
    user_name: str
    password: str
    email: EmailStr
    phone: str
    gender: str | None = None
```

**Step 2: 定义登录请求模型**

```python
class LoginRequest(BaseModel):
    account: str
    password: str
```

**Step 3: 定义 Token 返回模型**

```python
class TokenResponse(BaseModel):
    access_token: str
    token_type: str = "bearer"
    expires_in: int
    user: UserProfileResponse
```

**Step 4: 定义个人资料响应和更新模型**

允许更新的字段只包含 `user_name`、`phone`、`email`、`gender`、`avatar_url`、`bio`。

### Task 3: 实现安全模块与认证服务

**Files:**
- Create: `d:\数据库技术\大作业\SecondHand\backend\app\core\security.py`
- Create: `d:\数据库技术\大作业\SecondHand\backend\app\services\auth_service.py`
- Create: `d:\数据库技术\大作业\SecondHand\backend\app\services\user_service.py`
- Create: `d:\数据库技术\大作业\SecondHand\backend\app\api\deps.py`

**Step 1: 实现密码哈希**

封装：

```python
hash_password(password: str) -> str
verify_password(password: str, password_hash: str) -> bool
```

**Step 2: 实现 JWT 工具**

封装：

```python
create_access_token(user_id: int, role: str) -> str
decode_access_token(token: str) -> dict
```

**Step 3: 实现当前用户依赖**

在 `deps.py` 中提供：

```python
get_db()
get_current_user()
get_current_admin()
```

**Step 4: 实现认证服务**

认证服务负责：
- 注册时校验学号和邮箱唯一
- 密码加密
- 创建新用户
- 登录时允许学号或邮箱登录
- 登录成功更新时间 `last_login_time`

**Step 5: 实现资料服务**

用户资料服务负责读取当前用户信息和更新允许修改的字段。

### Task 4: 改造认证接口

**Files:**
- Modify: `d:\数据库技术\大作业\SecondHand\backend\app\api\routes\auth.py`
- Modify: `d:\数据库技术\大作业\SecondHand\backend\app\api\router.py`

**Step 1: 替换占位注册接口**

新增：

```python
POST /api/auth/register
```

请求体：

```json
{
  "student_no": "2023123456",
  "user_name": "张三",
  "password": "abc12345",
  "email": "2023123456@stu.edu.cn",
  "phone": "13800000000",
  "gender": "男"
}
```

**Step 2: 替换占位登录接口**

新增：

```python
POST /api/auth/login
```

支持 `account + password` 登录，`account` 可为学号或邮箱。

**Step 3: 新增获取当前用户接口**

```python
GET /api/auth/me
```

**Step 4: 新增更新个人资料接口**

```python
PUT /api/auth/me
```

**Step 5: 新增退出登录接口**

```python
POST /api/auth/logout
```

课程项目可以先做前端本地删除 token，后端返回成功即可。

### Task 5: 增加前端认证页面与状态管理

**Files:**
- Create: `d:\数据库技术\大作业\SecondHand\frontend\src\views\LoginView.vue`
- Create: `d:\数据库技术\大作业\SecondHand\frontend\src\views\RegisterView.vue`
- Create: `d:\数据库技术\大作业\SecondHand\frontend\src\views\ProfileView.vue`
- Create: `d:\数据库技术\大作业\SecondHand\frontend\src\composables\useAuth.js`
- Modify: `d:\数据库技术\大作业\SecondHand\frontend\src\api\http.js`
- Modify: `d:\数据库技术\大作业\SecondHand\frontend\src\router\index.js`
- Modify: `d:\数据库技术\大作业\SecondHand\frontend\src\components\layout\AppHeader.vue`
- Modify: `d:\数据库技术\大作业\SecondHand\frontend\src\components\layout\AppSidebar.vue`

**Step 1: 增加登录页**

字段：
- 学号或邮箱
- 密码

**Step 2: 增加注册页**

字段：
- 学号
- 姓名/昵称
- 邮箱
- 手机号
- 密码
- 确认密码
- 性别

**Step 3: 增加个人中心页**

展示：
- 学号
- 认证状态
- 角色
- 信誉分
- 创建时间

可编辑：
- 昵称
- 手机号
- 邮箱
- 性别
- 个人简介

**Step 4: 实现登录态管理**

`useAuth.js` 负责：
- 保存 token 和用户信息
- 提供 `login()`、`logout()`、`fetchMe()` 方法
- 从 `localStorage` 恢复登录态

**Step 5: 增加请求拦截器**

在 `http.js` 中自动给请求头加：

```js
Authorization: Bearer <token>
```

### Task 6: 增加前端路由守卫与权限控制

**Files:**
- Modify: `d:\数据库技术\大作业\SecondHand\frontend\src\router\index.js`

**Step 1: 为路由增加元信息**

```js
meta: { requiresAuth: true }
meta: { requiresAdmin: true }
```

**Step 2: 配置守卫**

规则：
- 未登录用户不可进入 `/publish`、`/orders`、`/profile`
- 非管理员不可进入 `/admin`
- 已登录用户访问 `/login` 和 `/register` 时自动跳回首页

**Step 3: 预期结果**

页面访问行为和课程需求中的“身份认证、角色权限”保持一致。

### Task 7: 初始化数据库 SQL 与演示数据

**Files:**
- Create: `d:\数据库技术\大作业\SecondHand\docs\sql\auth_user.sql`
- Create: `d:\数据库技术\大作业\SecondHand\docs\sql\auth_seed.sql`

**Step 1: 输出建表 SQL**

示例表结构：

```sql
CREATE TABLE user (
  user_id BIGINT PRIMARY KEY AUTO_INCREMENT,
  student_no VARCHAR(20) NOT NULL UNIQUE,
  user_name VARCHAR(50) NOT NULL,
  gender VARCHAR(10),
  phone VARCHAR(20),
  email VARCHAR(100) NOT NULL UNIQUE,
  password_hash VARCHAR(255) NOT NULL,
  role VARCHAR(20) NOT NULL DEFAULT 'student',
  credit_score INT NOT NULL DEFAULT 100,
  status VARCHAR(20) NOT NULL DEFAULT 'active',
  verify_status VARCHAR(20) NOT NULL DEFAULT 'verified',
  avatar_url VARCHAR(255),
  bio VARCHAR(255),
  create_time DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
  update_time DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
  last_login_time DATETIME NULL
);
```

**Step 2: 输出种子数据**

准备：
- 1 个学生账号
- 1 个管理员账号

### Task 8: 测试与验证

**Files:**
- Create: `d:\数据库技术\大作业\SecondHand\backend\tests\test_auth_api.py`
- Create: `d:\数据库技术\大作业\SecondHand\backend\tests\test_profile_api.py`

**Step 1: 注册接口测试**

覆盖：
- 正常注册
- 学号重复
- 邮箱重复
- 密码过短

**Step 2: 登录接口测试**

覆盖：
- 学号登录成功
- 邮箱登录成功
- 密码错误
- 不存在用户

**Step 3: 资料接口测试**

覆盖：
- 获取当前用户资料
- 修改允许字段成功
- 未登录访问失败

**Step 4: 前端手动验证清单**

- 注册成功后跳转登录页或直接登录
- 登录后头部显示当前用户
- 个人中心可更新资料
- 登出后受保护页面无法继续访问
