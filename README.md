# 极智协同 - FastAPI 后端

![Deploy](https://github.com/zzp-997/howtoai-backend/actions/workflows/deploy.yml/badge.svg)

极智协同办公系统后端服务，基于 FastAPI + MySQL，提供认证、会议预定、差旅申请、请假打卡、待办事项、公告通知、文档管理、审批、消息、任务协作等 API 接口。

## 技术栈

FastAPI · SQLAlchemy (异步) · MySQL · JWT (双 Token) · Docker

## 项目结构

```
app/
├── api/v1/              # API 路由
│   ├── auth.py         # 认证
│   ├── meetings.py     # 会议
│   ├── approvals.py    # 审批
│   ├── messages.py     # 消息中心
│   ├── feedbacks.py    # 意见反馈
│   ├── knowledge.py    # 知识库
│   ├── stats.py        # 数据统计
│   └── task.py         # 任务协作
├── core/               # 配置、数据库、安全
├── models/             # 数据模型
├── schemas/            # 请求/响应模型
├── services/          # 业务逻辑
└── main.py             # 应用入口
```

## 快速开始

```bash
# 安装依赖
pip install -r requirements.txt

# 配置 .env.local 中的数据库连接
# DATABASE_URL=mysql+aiomysql://用户名:密码@主机:3306/howtoai

# 启动服务（开发模式）
python run.py
```

API 文档：http://localhost:8000/docs

## 数据库迁移

```bash
# 初始化表结构
mysql -u root -p howtoai < sql/init_tables.sql

# 二期扩展表
mysql -u root -p howtoai < sql/migration_approval_message_feedback.sql
mysql -u root -p howtoai < sql/migration_knowledge_task_stats.sql
```

## API 概览

| 模块 | 前缀 | 说明 |
|------|------|------|
| 认证 | /api/v1/auth | 登录、登出、Token刷新 |
| 用户 | /api/v1/users | 用户管理 |
| 会议 | /api/v1/meeting-rooms, /api/v1/reservations | 会议室、预定 |
| 审批 | /api/v1/approvals | 审批流程 |
| 消息 | /api/v1/messages | 消息通知 |
| 反馈 | /api/v1/feedbacks | 意见反馈 |
| 知识库 | /api/v1/knowledge | 知识管理 |
| 任务 | /api/v1/tasks | 任务协作 |
| 统计 | /api/v1/stats | 数据统计 |

## 部署

推送 `master` 分支自动触发 GitHub Actions 部署，详见 [部署文档](deploy/DEPLOYMENT.md)。

## License

MIT
