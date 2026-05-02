# 设计：修复后端启动问题并实施二期审批模块

## Context

### 现状
后端已完成 Flask 到 FastAPI 的框架迁移（commit `fce809d feat: 二期迭代初步完成提交`），但存在以下问题：

1. **启动阻塞**：`audit_service.py` 使用 Flask 同步模式（`db.session.add()`），但被 `auth_service.py` 用 `await` 异步调用
2. **装饰器时序**：`RateLimitMiddleware` 的装饰器（`@rate_limit_login()`）在模块导入时求值，但 `init_app()` 在 `main.py` 中较晚才调用
3. **依赖缺失**：`requirements.txt` 缺少 Flask 相关依赖

### 约束
- 必须兼容现有 SQLAlchemy 2.0 异步架构
- 必须保持 API 路由注册在 `app/api/v1/__init__.py` 中
- 必须遵循现有分层架构：Router → Service → Model/Schema

## Goals / Non-Goals

**Goals:**
- 修复所有启动阻塞问题，使项目能正常启动
- 将遗留 Flask 代码正确迁移到 FastAPI 异步模式
- 实施二期审批模块（审批链、审批流程、审批记录）
- 实施二期消息中心（消息列表、已读未读）
- 实施二期意见反馈（提交、查询、回复）

**Non-Goals:**
- 不修改现有业务模块 API
- 不修改现有数据库表结构
- 不实施定时任务调度（催办提醒由前端触发）
- 不实施实时 WebSocket/SSE 通知

## Decisions

### Decision 1: audit_service.py 迁移策略

**选择**: 创建新的异步版本 `audit_service_v2.py`，原文件保留但不启用

**理由**:
- 原 `audit_service.py` 使用 Flask-SQLAlchemy 同步 API（`db.session.add()`）
- `auth_service.py` 中使用 `await AuditService.log_login()` 调用
- 直接修改风险较高，新文件隔离改动

**替代方案**:
- 方案A（选择）: 创建新文件，渐进式迁移
- 方案B: 直接修改原文件，改用 SQLAlchemy 异步 session
- 方案C: 移除 audit_service 依赖，简化登录服务

### Decision 2: 装饰器时序问题

**选择**: 调整 `main.py` 中 `init_app()` 的调用顺序

**理由**:
- `RateLimitMiddleware.init_app(app)` 必须在路由导入前调用
- FastAPI 的 `app.include_router()` 在导入时求值装饰器
- 解决方案：将限流中间件初始化移到路由注册之前

**代码调整**:
```python
# main.py 正确的初始化顺序
app = FastAPI(...)
RateLimitMiddleware.init_app(app)  # 先初始化限流
from app.api import api_router    # 再导入路由
app.include_router(api_router)    # 最后注册路由
```

### Decision 3: Flask 兼容层

**选择**: 移除 `app/extensions.py` 和 Flask 相关导入

**理由**:
- `audit_service.py` 已被 `rate_limit_middleware_fastapi.py` 替代（slowapi）
- Flask 依赖（flask, flask-sqlalchemy）仅用于兼容层，应移除
- 保持技术栈纯净：FastAPI + SQLAlchemy 2.0 async

### Decision 4: 审批模块数据模型

**选择**: 遵循文档 `数据库设计-审批模块.md` 的表结构，使用 SQLAlchemy 2.0 async ORM

**理由**:
- 文档已完整设计，无需重复设计
- 使用 `async_sessionmaker` 和 `AsyncSession`
- 外键关系使用 `relationship()` 的 `back_populates`

**表结构**:
- `approval_chains`: 审批链配置（一对多 → approval_nodes）
- `approval_nodes`: 审批节点（多对一 ← approval_requests）
- `approval_requests`: 审批申请（多对一 ← approval_records）
- `approval_records`: 审批记录
- `approval_reminders`: 催办记录
- `messages`: 消息
- `feedback`: 意见反馈

### Decision 5: API 路由注册

**选择**: 在 `app/api/v1/__init__.py` 中注册新路由

**理由**:
- 符合项目约定：所有 v1 API 在 `__init__.py` 中注册
- 便于统一管理前缀 `/api/v1/`

## Risks / Trade-offs

| Risk | Mitigation |
|------|------------|
| 直接修改 Flask 遗留代码可能引入回归 | 创建新文件隔离改动，保留原文件备份 |
| 异步 audit 服务可能遗漏日志 | 暂时保持简单实现，后续迭代完善 |
| 审批流程状态机复杂可能遗漏边界 | 先实现核心流程，复杂逻辑（会签、转交）后续迭代 |

## Migration Plan

### Phase 1: 修复启动阻塞
1. 修复 `main.py` 初始化顺序
2. 移除 Flask 兼容层和遗留导入
3. 验证项目能正常启动
4. 更新 `requirements.txt`

### Phase 2: 迁移 audit_service
1. 创建 `audit_service_v2.py`（异步版本）
2. 更新 `auth_service.py` 使用新服务
3. 验证登录日志记录正常

### Phase 3: 实施审批模块
1. 创建数据模型
2. 创建 Pydantic Schema
3. 创建 Service 层
4. 创建 API 路由
5. 注册路由

### Phase 4: 实施消息和反馈模块
同上结构

## Open Questions

1. **Q: 审批流程会签（多人同时审批）是否本次实施？**
   A: 否，暂不支持会签，只支持单人顺序审批

2. **Q: 审批超时自动通过是否实施？**
   A: 否，由前端触发催办，后端记录催办次数

3. **Q: 是否需要管理员角色权限控制？**
   A: 是，审批链配置需管理员权限，审批操作需审批人权限
