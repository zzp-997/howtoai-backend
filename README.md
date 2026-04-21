# 极智协同 - FastAPI 后端

![Deploy](https://github.com/zzp-997/howtoai-backend/actions/workflows/deploy.yml/badge.svg)

极智协同办公系统后端服务，基于 FastAPI + MySQL，提供认证、会议预定、差旅申请、请假打卡、待办事项、公告通知、文档管理、报销等 API 接口。

## 技术栈

FastAPI · SQLAlchemy · aiomysql · JWT · Docker

## 项目结构

```
app/
├── api/v1/          # API 路由
├── core/            # 配置、数据库、安全
├── models/          # 数据模型
├── schemas/         # 请求/响应模型
├── services/        # 业务逻辑
└── main.py          # 应用入口
```

## 快速开始

```bash
# 安装依赖
pip install -r requirements.txt

# 配置 .env 中的数据库连接
# DATABASE_URL=mysql+aiomysql://用户名:密码@主机:3306/howtoai

# 启动服务
python run.py
```

API 文档：http://localhost:8000/docs

## 部署

推送 `master` 分支自动触发 GitHub Actions 部署，详见 [部署文档](deploy/DEPLOYMENT.md)。

## License

MIT
