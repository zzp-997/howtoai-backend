## Context

后端 API 返回业务错误时存在两种不一致的模式：
1. `raise HTTPException(status_code=404, detail="报销单不存在")` — HTTP 4xx + body
2. `return ResponseModel(code=404, message="用户不存在", data=None)` — HTTP 200 + body.code ≠ 200

导致前端需要在 `responseInterceptorsCatch`（HTTP 状态码错误）和 `transformRequestHook`（body.code 错误）两条路径分别处理，增加维护成本。

此外，错误提示文案硬编码散落在 12 个 API 文件中（"报销单不存在"、"无权限"等），无统一枚举。

## Goals / Non-Goals

**Goals:**
- 业务错误统一走 HTTP 200 + body.code，前端只需一条路径处理
- 定义统一的 ErrorCode 枚举，消除硬编码
- 提供全局 BizException 异常处理器，自动转换为标准响应格式

**Non-Goals:**
- 错误上报/埋点
- 国际化错误文案
- 修改 HTTP 协议层错误处理（401/422/429/500）
- 修改 auth.py 中 get_current_user 的 401（FastAPI Depends 需要）

## Decisions

### D1: 业务错误统一走 HTTP 200 + body.code

**选择**：BizException 全局处理器返回 HTTP 200，body 中携带 code + message + data

**替代方案**：
- A) 继续 HTTP 4xx + body：前端需两条处理路径
- B) 完全移除 HTTP 状态码语义：与 RESTful 规范冲突

**理由**：HTTP 状态码用于协议层，业务错误用 body.code 区分，前端统一处理。

### D2: 错误码分段编码

**选择**：1xxxx 通用 / 2xxxx 认证权限 / 3xxxx 业务（301xx~311xx 按模块细分）

**理由**：分段编码便于快速定位模块，新增模块只需分配新段号。

### D3: BizException 保留 HTTPException 给协议层错误

**选择**：业务错误用 BizException，协议层错误（401 认证、422 参数、429 限流、5xx 服务端）仍用 HTTPException

**理由**：FastAPI Depends 机制（如 get_current_user）依赖 HTTP 401 触发认证流程，不能改为 body.code。

## 数据流图

```
API 层
  │
  ├── 业务错误 → raise BizException(ErrorCode.XXX)
  │       │
  │       ▼
  │   biz_exception_handler
  │       │
  │       ▼
  │   HTTP 200 { code: 30xx, message: "文案", data: null }
  │
  ├── 认证错误 → raise HTTPException(401)  [auth.py get_current_user]
  │       │
  │       ▼
  │   http_exception_handler
  │       │
  │       ▼
  │   HTTP 401 { code: 401, message: "...", data: null }
  │
  ├── 参数校验 → RequestValidationError
  │       │
  │       ▼
  │   validation_exception_handler
  │       │
  │       ▼
  │   HTTP 422 { code: 422, message: "字段: 错误", data: null }
  │
  └── 未知异常 → Exception
          │
          ▼
      general_exception_handler
          │
          ▼
      HTTP 500 { code: 500, message: "服务器内部错误", data: null }
```

## API 变更说明

### 业务错误响应（变更后）

所有业务错误统一返回 HTTP 200，body 格式：

```json
{
  "code": 30401,
  "message": "报销单不存在",
  "data": null
}
```

### HTTP 协议层错误（不变）

| HTTP 状态码 | 触发场景 | 响应格式 |
|---|---|---|
| 401 | Token 无效/未提供 | `{ code: 401, message: "...", data: null }` |
| 422 | 请求参数校验失败 | `{ code: 422, message: "字段: 错误", data: null }` |
| 429 | 限流 | HTTP 429 |
| 500 | 未知异常 | `{ code: 500, message: "服务器内部错误", data: null }` |

## Risks / Trade-offs

- **[BREAKING API 变更]** 业务错误从 HTTP 4xx 改为 HTTP 200 → 前端拦截器已同步适配，需前后端同时部署
- **[ErrorCode 膨胀]** 新增业务场景需持续补充 → 编码规则预留段号空间，新增成本低
- **[get_current_user 401 保留]** Depends 机制依赖 HTTP 状态码 → 保持不变

## Migration Plan

1. 后端先部署（新增文件不影响现有代码）
2. 前端部署（拦截器适配 HTTP 200 + body.code，同时兼容旧 HTTP 4xx）
3. 两端同时上线后生效

**回滚策略**：前端拦截器兼容 HTTP 4xx 和 body.code 两种模式，回滚后端时前端仍可工作。
