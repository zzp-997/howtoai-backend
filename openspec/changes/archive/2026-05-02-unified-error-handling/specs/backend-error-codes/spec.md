## ADDED Requirements

### Requirement: 统一业务错误码枚举
后端 SHALL 定义 `ErrorCode` 枚举类（`app/core/error_codes.py`），包含所有业务错误码。错误码 SHALL 按分段编码：1xxxx 通用、2xxxx 认证权限、3xxxx 业务逻辑（按模块细分 301xx~311xx）。每个错误码 SHALL 有对应的默认中文提示文案，定义在 `ERROR_MESSAGES` 字典中。

#### Scenario: 查询不存在的资源
- **WHEN** API 层查询到资源不存在
- **THEN** 抛出 `BizException(ErrorCode.XXX_NOT_FOUND)`，响应 HTTP 200 + body `{ code: 30xx, message: "资源不存在", data: null }`

#### Scenario: 无权限操作
- **WHEN** 用户尝试执行无权限的操作
- **THEN** 抛出 `BizException(ErrorCode.PERMISSION_DENIED)`，响应 HTTP 200 + body `{ code: 20003, message: "暂无权限", data: null }`

#### Scenario: 状态不允许操作
- **WHEN** 资源当前状态不允许执行操作（如修改已审批的报销单）
- **THEN** 抛出 `BizException(ErrorCode.XXX_STATUS_INVALID)`，响应包含业务错误码和对应提示文案

#### Scenario: 新增业务模块错误码
- **WHEN** 需要为新的业务模块添加错误码
- **THEN** 在 3xxxx 段中分配新的子段号（如 312xx），定义枚举值和默认文案

### Requirement: 统一业务异常类
后端 SHALL 定义 `BizException` 异常类（`app/core/exceptions.py`），接收 `ErrorCode` 和可选的 `message` 参数。当 `message` 为空时，SHALL 使用 `ERROR_MESSAGES` 中的默认文案。所有业务错误 SHALL 通过抛出 `BizException` 返回，不再使用 `HTTPException` 返回业务错误。

#### Scenario: 使用默认文案
- **WHEN** 抛出 `BizException(ErrorCode.EXPENSE_NOT_FOUND)` 且未传 message
- **THEN** 异常的 message 为 ERROR_MESSAGES 中的 "报销单不存在"

#### Scenario: 覆盖默认文案
- **WHEN** 抛出 `BizException(ErrorCode.RESERVATION_CONFLICT, "时间冲突，与预定 5 冲突")`
- **THEN** 异常的 message 为 "时间冲突，与预定 5 冲突"

### Requirement: 全局业务异常处理器
后端 SHALL 在 main.py 中注册 `BizException` 全局异常处理器，将 BizException 统一转换为 HTTP 200 响应，body 格式为 `{ code: <ErrorCode>, message: <文案>, data: null }`。HTTP 协议层错误（401 认证、422 参数校验、429 限流、500 服务端错误）SHALL 继续使用 HTTPException 和现有处理器。

#### Scenario: 业务异常响应格式
- **WHEN** API 层抛出 `BizException(ErrorCode.EXPENSE_NOT_FOUND)`
- **THEN** 响应 HTTP 200，body 为 `{ "code": 30401, "message": "报销单不存在", "data": null }`

#### Scenario: 认证异常仍走 HTTP 401
- **WHEN** get_current_user 依赖注入检测到无效 Token
- **THEN** 抛出 HTTPException(401)，由 http_exception_handler 处理，响应 HTTP 401

#### Scenario: 参数校验错误仍走 HTTP 422
- **WHEN** 请求参数不满足 Pydantic 校验
- **THEN** 由 RequestValidationError 处理器处理，响应 HTTP 422

### Requirement: API 层使用 BizException
后端所有 API 文件中的业务错误 HTTPException SHALL 替换为 BizException。auth.py 中 get_current_user 依赖注入的 401 HTTPException SHALL 保留不变（FastAPI Depends 机制需要）。

#### Scenario: 报销单接口改造
- **WHEN** 报销单不存在时
- **THEN** 抛出 `BizException(ErrorCode.EXPENSE_NOT_FOUND)` 而非 `HTTPException(404, "报销单不存在")`

#### Scenario: 认证依赖注入保留
- **WHEN** get_current_user 检测到无 Token
- **THEN** 仍抛出 `HTTPException(status_code=401)`
