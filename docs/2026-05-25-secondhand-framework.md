# SecondHand Framework Implementation Plan

> **For Claude:** REQUIRED SUB-SKILL: Use superpowers:executing-plans to implement this plan task-by-task.

**Goal:** 在 `SecondHand` 目录下搭建一个适合课程展示的校园二手交易平台前后端分离框架，包含基础页面、后端 API 骨架、配置文件与启动说明，但不实现复杂业务细节。

**Architecture:** 采用 `Vue 3 + Vite` 构建前端展示层，使用 `Vue Router` 组织首页、商品、发布、订单、管理等页面骨架；后端采用 `FastAPI`，按 `api/routes`、`core`、`schemas`、`services` 模块分层，提供可扩展的占位接口。目录结构强调清晰和可演示性，方便后续继续接入 MySQL、ORM 和业务逻辑。

**Tech Stack:** Vue 3, Vite, Vue Router, Axios, FastAPI, Uvicorn, Pydantic

---

### Task 1: 创建项目根目录与说明文件

**Files:**
- Create: `SecondHand/README.md`
- Create: `SecondHand/.gitignore`

**Step 1: 创建 `SecondHand` 目录**

新建项目根目录，作为前后端统一工作区。

**Step 2: 编写根说明文档**

说明项目定位、目录结构、启动方式和当前仅为框架版的范围边界。

**Step 3: 编写忽略规则**

覆盖前端 `node_modules`、构建产物以及后端虚拟环境与缓存文件。

### Task 2: 搭建 Vue 前端骨架

**Files:**
- Create: `SecondHand/frontend/package.json`
- Create: `SecondHand/frontend/vite.config.js`
- Create: `SecondHand/frontend/index.html`
- Create: `SecondHand/frontend/src/main.js`
- Create: `SecondHand/frontend/src/App.vue`
- Create: `SecondHand/frontend/src/router/index.js`
- Create: `SecondHand/frontend/src/api/http.js`
- Create: `SecondHand/frontend/src/styles.css`
- Create: `SecondHand/frontend/src/components/layout/AppHeader.vue`
- Create: `SecondHand/frontend/src/components/layout/AppSidebar.vue`
- Create: `SecondHand/frontend/src/views/HomeView.vue`
- Create: `SecondHand/frontend/src/views/ProductsView.vue`
- Create: `SecondHand/frontend/src/views/PublishView.vue`
- Create: `SecondHand/frontend/src/views/OrdersView.vue`
- Create: `SecondHand/frontend/src/views/AdminView.vue`

**Step 1: 初始化前端依赖声明**

定义 Vue、Vue Router、Axios 与 Vite 的依赖和脚本。

**Step 2: 编写应用入口与路由**

建立单页应用入口，配置 5 个课程演示页面。

**Step 3: 编写布局组件**

添加顶部导航和侧边功能菜单，形成统一展示框架。

**Step 4: 编写页面占位内容**

为首页、商品、发布、订单、后台分别放置模块卡片，体现后续可扩展的业务区域。

### Task 3: 搭建 FastAPI 后端骨架

**Files:**
- Create: `SecondHand/backend/requirements.txt`
- Create: `SecondHand/backend/app/main.py`
- Create: `SecondHand/backend/app/core/config.py`
- Create: `SecondHand/backend/app/api/router.py`
- Create: `SecondHand/backend/app/api/routes/health.py`
- Create: `SecondHand/backend/app/api/routes/auth.py`
- Create: `SecondHand/backend/app/api/routes/products.py`
- Create: `SecondHand/backend/app/api/routes/orders.py`
- Create: `SecondHand/backend/app/api/routes/admin.py`
- Create: `SecondHand/backend/app/schemas/common.py`
- Create: `SecondHand/backend/app/services/dashboard_service.py`

**Step 1: 编写应用入口**

配置 FastAPI 实例、跨域、基础元信息和根路径响应。

**Step 2: 拆分路由模块**

将健康检查、认证、商品、订单、后台统计接口拆到独立路由文件。

**Step 3: 编写公共响应模型**

定义统一返回结构，便于后续接口扩展。

**Step 4: 编写占位服务层**

提供仪表盘和统计数据的示例输出，避免路由层堆积逻辑。

### Task 4: 完善联调配置与文档

**Files:**
- Create: `SecondHand/frontend/.env.example`
- Create: `SecondHand/backend/.env.example`
- Modify: `SecondHand/README.md`

**Step 1: 添加环境变量模板**

前端配置 API 基础地址，后端配置应用名、版本和 CORS 源。

**Step 2: 更新启动说明**

写明开发环境、安装命令、运行顺序和后续扩展方向。

### Task 5: 进行基础验证

**Files:**
- Verify: `SecondHand/frontend`
- Verify: `SecondHand/backend`

**Step 1: 检查前端关键文件语法**

确保 `Vue` 页面、路由与配置文件无明显语法问题。

**Step 2: 检查后端关键文件语法**

确保 `FastAPI` 入口、路由与模型可正常导入。

**Step 3: 运行诊断工具**

检查最近编辑文件是否出现 IDE 级别诊断错误。
