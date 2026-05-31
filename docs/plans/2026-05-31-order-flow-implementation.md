# Order Flow Implementation Plan

> **For Claude:** REQUIRED SUB-SKILL: Use superpowers:executing-plans to implement this plan task-by-task.

**Goal:** 为校园二手交易平台实现“订单创建、状态流转、成交确认和评价反馈”的完整课程版能力，并支持前端直接操作演示。

**Architecture:** 后端继续使用 FastAPI + SQLAlchemy，在现有认证体系上新增 `product`、`order_info`、`review` 三张核心表和对应服务层，实现订单状态机与评价约束；前端在商品页和订单页接入真实接口，实现下单、确认、完成和评价的交互闭环。数据库初始化脚本同步进入仓库和 Docker MySQL 初始化目录，确保所有协作者使用同一套表结构和种子数据。

**Tech Stack:** Vue 3, Vue Router, Axios, FastAPI, SQLAlchemy, PyMySQL, MySQL 8.4, pytest

---

### Task 1: 扩展数据库初始化脚本与后端模型

**Files:**
- Modify: `d:\数据库技术\大作业\SecondHand\database\mysql\init\01_auth_user.sql`
- Modify: `d:\数据库技术\大作业\SecondHand\database\mysql\init\02_auth_seed.sql`
- Modify: `d:\数据库技术\大作业\SecondHand\docs\sql\auth_user.sql`
- Modify: `d:\数据库技术\大作业\SecondHand\docs\sql\auth_seed.sql`
- Create: `d:\数据库技术\大作业\SecondHand\backend\app\models\product.py`
- Create: `d:\数据库技术\大作业\SecondHand\backend\app\models\order_info.py`
- Create: `d:\数据库技术\大作业\SecondHand\backend\app\models\review.py`
- Modify: `d:\数据库技术\大作业\SecondHand\backend\app\db\base.py`

**Step 1: 写建表 SQL**

新增：
- `product`
- `order_info`
- `review`

**Step 2: 写种子数据**

为学生卖家准备至少 2 个在售商品，便于前端下单演示。

**Step 3: 创建 SQLAlchemy 模型**

模型字段要覆盖：
- 商品状态：`ON_SALE` / `LOCKED` / `SOLD` / `OFFLINE`
- 订单状态：`PENDING` / `IN_PROGRESS` / `COMPLETED` / `CANCELLED`

**Step 4: 注册模型**

确保 `Base.metadata.create_all()` 能创建新增表。

### Task 2: 设计商品、订单、评价的 Schema

**Files:**
- Create: `d:\数据库技术\大作业\SecondHand\backend\app\schemas\product.py`
- Create: `d:\数据库技术\大作业\SecondHand\backend\app\schemas\order.py`
- Create: `d:\数据库技术\大作业\SecondHand\backend\app\schemas\review.py`

**Step 1: 定义商品返回模型**

包含：
- 商品 id、标题、价格、状态、卖家信息、交易地点

**Step 2: 定义订单相关模型**

包含：
- 创建订单请求
- 订单响应
- 状态流转响应

**Step 3: 定义评价模型**

包含：
- 新增评价请求
- 评价返回

### Task 3: 实现商品、订单、评价服务层

**Files:**
- Create: `d:\数据库技术\大作业\SecondHand\backend\app\services\product_service.py`
- Create: `d:\数据库技术\大作业\SecondHand\backend\app\services\order_service.py`
- Create: `d:\数据库技术\大作业\SecondHand\backend\app\services\review_service.py`

**Step 1: 商品服务**

支持：
- 查询商品列表
- 查询商品详情
- 创建演示商品

**Step 2: 订单服务**

支持：
- 买家创建订单
- 卖家确认订单
- 买家确认成交
- 买家或卖家取消订单

约束：
- 不能购买自己的商品
- 只有 `ON_SALE` 商品可下单
- 一个商品锁定后不能重复下单

**Step 3: 评价服务**

支持：
- 仅在订单完成后评价
- 同一订单仅允许评价一次
- 评价后返回更新后的评价记录

### Task 4: 改造产品、订单和评价 API

**Files:**
- Modify: `d:\数据库技术\大作业\SecondHand\backend\app\api\routes\products.py`
- Modify: `d:\数据库技术\大作业\SecondHand\backend\app\api\routes\orders.py`
- Create: `d:\数据库技术\大作业\SecondHand\backend\app\api\routes\reviews.py`
- Modify: `d:\数据库技术\大作业\SecondHand\backend\app\api\router.py`

**Step 1: 商品接口**

新增：
- `GET /api/products`
- `POST /api/products`

**Step 2: 订单接口**

新增：
- `GET /api/orders`
- `POST /api/orders`
- `PATCH /api/orders/{order_id}/confirm`
- `PATCH /api/orders/{order_id}/complete`
- `PATCH /api/orders/{order_id}/cancel`

**Step 3: 评价接口**

新增：
- `POST /api/reviews`
- `GET /api/reviews/order/{order_id}`

### Task 5: 实现前端商品下单能力

**Files:**
- Modify: `d:\数据库技术\大作业\SecondHand\frontend\src\views\ProductsView.vue`
- Create: `d:\数据库技术\大作业\SecondHand\frontend\src\api\orders.js`
- Create: `d:\数据库技术\大作业\SecondHand\frontend\src\api\products.js`

**Step 1: 商品页拉取真实商品**

用真实接口替换当前静态数组。

**Step 2: 商品页增加下单按钮**

仅当：
- 已登录
- 当前用户不是卖家
- 商品状态为 `ON_SALE`

时允许下单。

**Step 3: 下单成功提示**

成功后刷新商品状态和订单列表入口提示。

### Task 6: 实现前端订单管理与评价交互

**Files:**
- Modify: `d:\数据库技术\大作业\SecondHand\frontend\src\views\OrdersView.vue`
- Create: `d:\数据库技术\大作业\SecondHand\frontend\src\api\reviews.js`

**Step 1: 订单页拉取真实订单**

区分：
- 买家订单
- 卖家订单

**Step 2: 根据角色和状态展示按钮**

例如：
- 卖家对 `PENDING` 订单可“确认接单”
- 买家对 `IN_PROGRESS` 订单可“确认成交”
- 买家对 `COMPLETED` 且未评价订单可“提交评价”

**Step 3: 增加评价表单**

字段：
- 评分
- 评价内容

### Task 7: 补充测试与验证

**Files:**
- Create: `d:\数据库技术\大作业\SecondHand\backend\tests\test_order_api.py`
- Create: `d:\数据库技术\大作业\SecondHand\backend\tests\test_review_api.py`

**Step 1: 订单测试**

覆盖：
- 创建订单成功
- 不允许购买自己的商品
- 卖家确认订单成功
- 买家确认成交成功
- 非法状态流转失败

**Step 2: 评价测试**

覆盖：
- 完成订单后评价成功
- 未完成订单不能评价
- 同一订单不能重复评价

**Step 3: 前端验证**

检查：
- 商品页可下单
- 订单页可状态流转
- 完成订单后可评价
- 页面刷新后数据状态一致
