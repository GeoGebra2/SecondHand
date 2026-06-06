# 校园二手交易平台框架

这是一个基于 `Vue 3 + FastAPI` 的校园二手交易平台课程项目框架，适合在现有数据库大作业方案基础上继续扩展。

## 当前范围

- 已搭建前端页面骨架、路由结构和基础样式
- 已搭建后端 API 分层结构和示例接口
- 已预留环境变量和后续接入数据库的位置
- 当前不包含完整业务逻辑、数据库连接和鉴权细节

## 目录结构

```text
SecondHand/
├─ database/                 # MySQL 初始化脚本
├─ frontend/
├─ backend/
├─ docker-compose.yml        # 一键启动数据库
└─ README.md
```

## 数据库启动

项目仓库内已经包含统一的 MySQL 初始化文件，团队成员可以直接使用同一套数据库结构和演示数据。

```bash
docker compose up -d mysql
```

启动后可使用以下连接信息：

- 主机：`127.0.0.1`
- 端口：`3307`
- 数据库：`secondhand`
- 用户名：`secondhand_user`
- 密码：`secondhand123`

数据库会自动导入以下内容：

- 用户认证表结构：`database/mysql/init/01_auth_user.sql`
- 演示账号数据：`database/mysql/init/02_auth_seed.sql`

演示账号：

- 学生账号：`student@campus.edu` / `student123`
- 管理员账号：`admin@campus.edu` / `admin12345`

后端启动前，建议先复制环境变量模板：

```bash
cd backend
copy .env.example .env
```

## 前端启动

```bash
cd frontend
npm install
npm run dev
```

## 后端启动

```bash
cd backend
python -m venv .venv
.venv\Scripts\activate
pip install -r requirements.txt
uvicorn app.main:app --reload
```

如果要重启并更新docker，需执行指令：
```bash
docker compose down-v
docker composeup-dmysgl
```

## 后续建议

- 接入 MySQL 和 ORM
- 实现用户、商品、订单、评价、举报等真实业务接口
- 将前端页面与后端接口对接，替换占位数据
