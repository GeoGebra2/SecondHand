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
├─ frontend/
├─ backend/
└─ README.md
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

## 后续建议

- 接入 MySQL 和 ORM
- 实现用户、商品、订单、评价、举报等真实业务接口
- 将前端页面与后端接口对接，替换占位数据
