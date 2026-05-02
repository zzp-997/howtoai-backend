## Why

后端 API 混用 HTTPException(4xx) 和 ResponseModel(code=xxx) 两种模式返回业务错误，前端需两条路径处理；错误码和提示文案在各 API 文件中硬编码散落，无统一枚举，难以维护。

## What Changes

- 新增 `ErrorCode` 统一业务错误码枚举（1xxxx 通用/2xxxx 认证/3xxxx 业务按模块细分）和 `ERROR_MESSAGES` 默认文案映射
- 新增 `BizException` 业务异常类，接收 ErrorCode + 可选自定义 message
- main.py 新增 BizException 全局异常处理器，业务错误统一走 HTTP 200 + body.code 返回
- API 层将散落的 `HTTPException(400/403/404)` 替换为 `BizException(ErrorCode.XXX)`
- auth.py 中 get_current_user 的 401 HTTPException 保留（FastAPI Depends 机制需要）

## Capabilities

### New Capabilities
- `backend-error-codes`: 统一业务错误码枚举 + BizException 异常体系 + 全局异常处理器 + API 层替换

### Modified Capabilities
<!-- 无已有 spec 需要修改 -->

## Impact

- **影响范围**：全部 API 接口（用户端 + 管理端）
- **新增文件**：`app/core/error_codes.py`、`app/core/exceptions.py`
- **改造文件**：`app/main.py`（新增处理器）、`app/api/v1/` 下 12 个文件替换 HTTPException
- **API 兼容性**：**BREAKING** — 业务错误响应从 HTTP 4xx 改为 HTTP 200 + body.code，前端拦截器需同步适配

## 非目标

- 不做错误上报/埋点
- 不做国际化错误文案（当前仅中文）
- 不改动 auth.py 中 get_current_user 的 401 HTTPException（FastAPI Depends 机制依赖）
- 不改动 HTTP 协议层错误的处理逻辑（401/422/429/500）
