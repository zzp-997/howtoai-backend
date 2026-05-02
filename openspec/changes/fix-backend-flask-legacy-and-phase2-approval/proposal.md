# 提案：修复后端启动问题并实施二期审批模块

## Why

后端已完成 Flask 到 FastAPI 的框架迁移，但遗留的 Flask 代码（`audit_service.py`）未正确迁移为异步模式，且限流中间件的装饰器在模块导入时求值导致启动失败。二期审批模块的文档已完成但代码未实施。前端正在等待后端 API 就绪。

## What Changes

### 1. 修复启动阻塞问题
- 将 `audit_service.py` 从 Flask 同步模式转换为 FastAPI 异步模式
- 修复 `RateLimitMiddleware` 装饰器在模块导入时求值的时序问题
- 补充 `requirements.txt` 缺失的依赖（flask, flask-sqlalchemy, flask-limiter, pyjwt）

### 2. 实施二期审批模块
- 审批链配置（ApprovalChain）
- 审批节点管理（ApprovalNode）
- 审批申请流程（ApprovalRequest）
- 审批记录（ApprovalRecord）
- 催办提醒（ApprovalReminder）

### 3. 实施二期消息中心
- 消息推送（Message）
- 未读角标
- 消息设置

### 4. 实施二期意见反馈
- 反馈提交（Feedback）
- 进度查询
- 管理员回复

## Capabilities

### New Capabilities
- `audit-service-async`: 将操作日志审计服务从 Flask 同步转换为 FastAPI 异步模式
- `approval-chain`: 审批链配置管理（创建、更新、删除、查询审批链）
- `approval-request`: 审批申请流程（提交、通过、拒绝、批量审批）
- `approval-reminder`: 催办提醒功能
- `message-center`: 消息中心（消息列表、已读未读状态）
- `feedback-module`: 意见反馈（提交、查询、回复）

### Modified Capabilities
- （空 - 本次不涉及已有能力的需求变更）

## Impact

### 受影响代码
- `app/core/security_module/audit_service.py` - 需重写为异步
- `app/core/security_module/rate_limit_middleware_fastapi.py` - 装饰器时序修复
- `app/main.py` - 初始化顺序调整
- `app/extensions.py` - Flask 兼容层（如需保留）

### 新增模块
- `app/models/approval.py` - 审批相关模型
- `app/schemas/approval.py` - 审批 Pydantic Schema
- `app/services/approval_service.py` - 审批业务逻辑
- `app/api/v1/approval.py` - 审批 API 路由
- `app/models/message.py` - 消息模型
- `app/schemas/message.py` - 消息 Schema
- `app/services/message_service.py` - 消息业务逻辑
- `app/api/v1/message.py` - 消息 API 路由
- `app/models/feedback.py` - 反馈模型
- `app/schemas/feedback.py` - 反馈 Schema
- `app/services/feedback_service.py` - 反馈业务逻辑
- `app/api/v1/feedback.py` - 反馈 API 路由

### 依赖变更
- `requirements.txt` - 添加 flask, flask-sqlalchemy, flask-limiter, pyjwt

### 数据库
- 需要创建新表：approval_chains, approval_nodes, approval_requests, approval_records, approval_reminders, messages, feedback

## 非目标

- 不修改现有业务模块的 API（用户认证、会议室、差旅、请假、考勤等）
- 不修改现有数据库表结构
- 不实施定时任务（催办提醒的后台调度）
- 不实施消息推送的实时通知（WebSocket/SSE）
