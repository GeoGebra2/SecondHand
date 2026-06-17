# 校园二手交易平台数据库管理系统

这是一个基于 `Vue 3 + FastAPI + MySQL` 的校园二手交易平台数据库大作业项目，面向“校园内部二手交易”场景，已经实现了用户认证、商品管理、订单流转、评价反馈、收藏通知、智能商品推荐和后台统计等核心功能。

项目重点不只是页面展示，而是通过一个真实业务场景体现数据库课程中的需求分析、关系建模、外键约束、索引设计、事务控制、统计查询与接口测试能力。

## 已实现功能

- 用户注册、登录、退出登录、个人资料查看与更新
- 商品分类管理，使用 `category_id` 外键关联商品
- 商品发布、编辑、下架、重新上架、图片列表展示
- 商品大厅查询，支持关键字、分类、价格区间和排序筛选
- 订单创建、卖家确认、买家完成、双方取消
- 买家评价卖家，并同步更新卖家信誉分
- 商品收藏、个人收藏夹、站内通知提醒
- 智能商品推荐，结合收藏、浏览、下单、类别偏好、价格区间和平台热度生成“猜你喜欢”
- 管理后台统计，包括热门分类、活跃用户、成交趋势
- 后端接口测试，覆盖商品、推荐、收藏通知等主流程

## 技术栈

- 前端：`Vue 3`、`Vue Router`、`Axios`、`Vite`
- 后端：`FastAPI`、`SQLAlchemy`
- 数据库：`MySQL 8.0`
- 测试：`pytest`

## 目录结构

```text
SecondHand/
├─ backend/                 # FastAPI 后端与接口测试
├─ frontend/                # Vue 3 前端页面
├─ database/mysql/init/     # MySQL 初始化脚本
├─ docs/                    # 报告与 SQL 文档
├─ docker-compose.yml       # 一键启动 MySQL
└─ README.md
```

## 数据库结构

当前核心数据表包括：

- `user`
- `category`
注意：初始化脚本（`database/mysql/init/*`）只会在数据库数据卷为空时由 MySQL 容器的
`docker-entrypoint-initdb.d` 自动执行（也就是首次启动时）。如果该卷已经存在，
这些脚本将不会被重复执行。对于增量模式，仓库内的 `database/mysql/migrations` 文件夹
存放可运行的迁移脚本。启动数据库后，请运行：

```powershell
docker-compose run --rm migrate
```

这样可以确保所有仓库中新增的表结构或数据修复脚本被应用到本地数据库。
- `order_info`
- `review`
- `favorite`
- `notification`
- `browse_history`

其中商品与分类采用外键设计：

- `product.category_id -> category.category_id`

这样比直接保存分类名称更规范，也便于分类改名、统计和索引优化。

## 数据库启动

```bash
docker compose up -d mysql
```

启动后连接信息如下：

- 主机：`127.0.0.1`
- 端口：`3307`
- 数据库：`secondhand`
- 用户名：`secondhand_user`
- 密码：`secondhand123`

初始化脚本会自动导入：

- 表结构：`database/mysql/init/01_auth_user.sql`
- 演示账号与种子数据：`database/mysql/init/02_auth_seed.sql`
- 编码修复脚本：`database/mysql/init/03_fix_seed_encoding.sql`
- 收藏、通知与浏览记录表：`database/mysql/init/04_my_task_tables.sql`

演示账号：

- 学生账号：`student@campus.edu` / `student123`
- 管理员账号：`admin@campus.edu` / `admin12345`

初始化种子数据额外包含：

- `6` 个演示用户
- `6` 个商品分类
- `54` 个商品
- 收藏、订单、浏览记录、通知等推荐训练样本

## 后端启动

首次启动建议先复制环境变量模板：

```bash
cd backend
copy .env.example .env
```

然后启动后端：

```bash
docker compose up -d mysql
cd backend
python -m venv .venv
.venv\Scripts\activate
pip install -r requirements.txt
uvicorn app.main:app --reload
```

如果后端启动时报 `Can't connect to MySQL server on '127.0.0.1'`，通常表示 MySQL 容器尚未启动，先执行上面的 `docker compose up -d mysql`，再确认 `backend/.env` 中的 `DATABASE_URL` 使用的是 `127.0.0.1:3307`。

默认接口地址：

- `http://127.0.0.1:8000/api`

## 前端启动

```bash
cd frontend
npm install
npm run dev
```

默认前端地址：

- `http://127.0.0.1:5173`

## 主要接口

认证与资料：

- `POST /api/auth/register`
- `POST /api/auth/login`
- `GET /api/auth/me`
- `PUT /api/auth/me`

商品与分类：

- `GET /api/products`
- `POST /api/products`
- `GET /api/products/mine`
- `PUT /api/products/{product_id}`
- `PATCH /api/products/{product_id}/offline`
- `PATCH /api/products/{product_id}/relist`
- `GET /api/products/categories`
- `POST /api/products/categories`
- `PUT /api/products/categories/{category_id}`

订单与评价：

- `GET /api/orders`
- `POST /api/orders`
- `PATCH /api/orders/{order_id}/confirm`
- `PATCH /api/orders/{order_id}/complete`
- `PATCH /api/orders/{order_id}/cancel`
- `POST /api/reviews`
- `GET /api/reviews/order/{order_id}`

收藏、通知与统计：

- `GET /api/favorites`
- `POST /api/favorites`
- `GET /api/notifications`
- `POST /api/notifications`
- `GET /api/recommendations`
- `POST /api/recommendations/browse-history`
- `GET /api/admin/dashboard`

推荐接口说明：

- `GET /api/recommendations`
  返回基于轻量级 AI 混合推荐模型生成的商品列表，并提供 `ai_score`、`ai_reason`、`ai_tags`
- `POST /api/recommendations/browse-history`
  记录登录用户浏览过的商品，用于后续个性化推荐

## 已验证测试

在 `backend` 目录下运行：

```bash
.venv\Scripts\python.exe -m pytest tests\test_recommendation_api.py tests\test_product_api.py tests\test_social_api.py
```

当前结果：

- `13 passed`

## 项目亮点

- 使用外键而非分类名称字符串维护商品分类关系
- 订单状态与商品状态联动，体现事务型业务流程
- 收藏和通知接口已并入正式鉴权体系，不再使用旁路接口
- 新增 `browse_history` 行为表，支持基于用户行为的可解释推荐
- 推荐模块采用“类别偏好 + 价格相似 + 热度分析 + 协同偏好”的轻量 AI 混合策略
- 后台统计直接基于数据库聚合结果生成，不是纯前端假数据
- 具备可演示、可测试、可写入大作业报告的完整闭环

## 说明

如果需要重新初始化数据库，可先停止并删除旧容器与卷，再重新启动：

```bash
docker compose down -v
docker compose up -d mysql
```

如需提交课程成果，建议配合仓库中的报告文档：

- `docs/校园二手交易平台数据库管理系统-大作业报告.md`
