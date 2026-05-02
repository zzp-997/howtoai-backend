# 任务清单：修复后端启动问题并实施二期审批模块

## 1. 修复启动阻塞问题

- [x] 1.1 调整 `app/main.py` 初始化顺序：将 `RateLimitMiddleware.init_app(app)` 移到路由导入之前
- [x] 1.2 移除 `app/extensions.py` Flask 兼容层
- [x] 1.3 更新 `requirements.txt` 添加缺失依赖：flask, flask-sqlalchemy, flask-limiter, pyjwt
- [x] 1.4 验证项目能正常启动

## 2. 迁移 audit_service 到异步模式

- [x] 2.1 创建 `app/core/security_module/audit_service_v2.py` 异步版本
- [x] 2.2 使用 SQLAlchemy AsyncSession 替代 Flask-SQLAlchemy db.session
- [x] 2.3 更新 `app/services/auth_service.py` 使用新的 audit 服务
- [x] 2.4 验证登录日志记录正常

## 3. 实施审批模块 - 数据模型

- [x] 3.1 创建 `app/models/approval.py`：ApprovalChain, ApprovalNode, ApprovalRequest, ApprovalRecord, ApprovalReminder
- [x] 3.2 创建 `app/models/message.py`：Message 模型
- [x] 3.3 创建 `app/models/feedback.py`：Feedback 模型
- [x] 3.4 创建数据库迁移 SQL 脚本

## 4. 实施审批模块 - Schema

- [x] 4.1 创建 `app/schemas/approval.py`：ApprovalChainSchema, ApprovalNodeSchema, ApprovalRequestSchema 等
- [x] 4.2 创建 `app/schemas/message.py`：MessageSchema, MessageQuerySchema 等
- [x] 4.3 创建 `app/schemas/feedback.py`：FeedbackSchema, FeedbackReplySchema 等

## 5. 实施审批模块 - Service

- [x] 5.1 创建 `app/services/approval_service.py`：ApprovalService 类
- [x] 5.2 创建 `app/services/message_service.py`：MessageService 类
- [x] 5.3 创建 `app/services/feedback_service.py`：FeedbackService 类

## 6. 实施审批模块 - API 路由

- [x] 6.1 创建 `app/api/v1/approval.py`：审批链 CRUD、审批申请、审批操作 API
- [x] 6.2 创建 `app/api/v1/message.py`：消息中心 API
- [x] 6.3 创建 `app/api/v1/feedback.py`：意见反馈 API

## 7. 注册路由

- [x] 7.1 在 `app/api/v1/__init__.py` 中注册 approval, message, feedback 路由
- [x] 7.2 验证所有 API 路由正常工作

## 8. 验证和测试

- [x] 8.1 启动项目验证无错误
- [x] 8.2 测试登录接口验证日志记录
- [x] 8.3 测试审批链创建接口
- [x] 8.4 测试消息中心接口
- [x] 8.5 测试意见反馈接口
