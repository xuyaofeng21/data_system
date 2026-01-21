# 企业业务流程数据管理及其资源配置系统 (Graduation Project)

## 项目简介
本项目是一个基于 **Vue 3 + FastAPI** 的企业业务流程数据管理系统。该系统旨在解决传统业务流程管理中数据采集不全、监控滞后等问题，通过结合 **机器学习算法**（Random Forest），实现对任务执行时长的智能预测与资源优化配置。

## 技术栈
- **前端**: Vue 3, Vite, Element Plus, ECharts, Pinia, Axios
- **后端**: Python 3.9+, FastAPI, SQLAlchemy
- **数据库**: MySQL (默认开发环境使用 SQLite 为了演示方便，可配置为 MySQL)
- **算法**: Scikit-learn (用于任务时长预测)

## 快速开始

### 1. 环境准备
确保已安装：
- Python 3.9+
- Node.js 16+
- MySQL 8.0 (可选，默认使用 SQLite)

### 2. 后端启动 (Backend)
```bash
cd backend

# 1. 安装依赖
pip install -r requirements.txt

# 2. 启动服务 (默认端口 8000)
# 在项目根目录下运行:
uvicorn backend.main:app --reload
```
后端 API 文档地址: http://127.0.0.1:8000/docs

### 3. 前端启动 (Frontend)
```bash
cd frontend

# 1. 安装依赖
npm install

# 2. 启动开发服务器
npm run dev
```
前端访问地址: http://localhost:5173

## 🔑 登录账号 (Login Credentials)

系统初始化时已包含一个管理员账号（如果您运行了测试脚本或手动注册）：

- **用户名 (Username)**: `admin`
- **密码 (Password)**: `password123`

> 如果提示账号不存在，请点击登录页面的 "Register New Account" 注册一个新账号即可。

## 功能使用指南

1.  **控制台 (Dashboard)**:
    - 登录后首页，查看当前活跃的流程实例数量。
    - 查看 **预测时长 vs 实际时长** 的对比图表（验证算法有效性）。

2.  **流程模型管理 (Process Models)**:
    - 点击 "Create New Process Model"。
    - 输入流程名称（如 "采购审批"）。
    - 定义节点 JSON (例如: `{"nodes": [{"id": "申请"}, {"id": "审批"}, {"id": "结束"}]}`)。

3.  **任务执行 (Task Execution)**:
    - 在模型列表点击 "Start Instance" 启动流程。
    - 进入 "Task Execution" 页面查看待办任务。
    - 系统会自动显示当前步骤的 **AI 预测耗时**。
    - 点击 "Complete Task" 完成任务，系统将记录实际耗时并用于后续模型训练。

## 目录结构
```
data_system/
├── backend/            # FastAPI 后端代码
│   ├── auth.py         # 认证模块
│   ├── database.py     # 数据库连接
│   ├── main.py         # 入口文件
│   ├── models.py       # 数据库模型
│   ├── prediction.py   # 机器学习预测模块
│   └── ...
├── frontend/           # Vue 3 前端代码
│   ├── src/
│   │   ├── views/      # 页面组件 (Dashboard, Login, etc.)
│   │   ├── styles/     # 样式文件 (Electric Blue 主题)
│   │   └── ...
└── README.md           # 说明文档
```
