## 1. 错误码与异常体系

- [x] 1.1 新增 `app/core/error_codes.py`：定义 ErrorCode 枚举（1xxxx/2xxxx/3xxxx）和 ERROR_MESSAGES 映射
- [x] 1.2 新增 `app/core/exceptions.py`：定义 BizException 类，接收 ErrorCode + 可选 message

## 2. 全局异常处理器

- [x] 2.1 改造 `app/main.py`：导入 BizException，新增 biz_exception_handler（HTTP 200 + body.code）

## 3. API 层 BizException 替换

- [x] 3.1 改造 `app/api/v1/expenses.py`：7 处 HTTPException → BizException（EXPENSE_NOT_FOUND / PERMISSION_DENIED / EXPENSE_STATUS_INVALID）
- [x] 3.2 改造 `app/api/v1/reservations.py`：6 处替换（RESERVATION_NOT_FOUND / PERMISSION_DENIED / RESERVATION_CONFLICT）
- [x] 3.3 改造 `app/api/v1/meeting_rooms.py`：6 处替换（ROOM_NOT_FOUND / PERMISSION_DENIED）
- [x] 3.4 改造 `app/api/v1/attendance.py`：4 处替换（MAKEUP_NOT_FOUND / PERMISSION_DENIED / MAKEUP_OPERATION_FAILED）
- [x] 3.5 改造 `app/api/v1/documents.py`：4 处替换（DOCUMENT_NOT_FOUND / PERMISSION_DENIED / DOCUMENT_PERMISSION_DENIED）
- [x] 3.6 改造 `app/api/v1/approval.py`：9 处替换（APPROVAL_CHAIN_NOT_FOUND / APPROVAL_NOT_FOUND / APPROVAL_OPERATION_FAILED）
- [x] 3.7 改造 `app/api/v1/leaves.py`：11 处替换（LEAVE_NOT_FOUND / PERMISSION_DENIED / LEAVE_DATE_CONFLICT / LEAVE_STATUS_INVALID）
- [x] 3.8 改造 `app/api/v1/trips.py`：9 处替换（TRIP_NOT_FOUND / PERMISSION_DENIED / TRIP_STATUS_INVALID）
- [x] 3.9 改造 `app/api/v1/configs.py`：15 处替换（TEMPLATE_NOT_FOUND / CITY_NOT_FOUND / HOLIDAY_NOT_FOUND / PERMISSION_DENIED）
- [x] 3.10 改造 `app/api/v1/announcements.py`：6 处替换（ANNOUNCEMENT_NOT_FOUND / PERMISSION_DENIED）
- [x] 3.11 改造 `app/api/v1/todos.py`：4 处替换（TODO_NOT_FOUND）
- [x] 3.12 改造 `app/api/v1/users.py`：5 处替换（USER_NOT_FOUND / PERMISSION_DENIED）
- [x] 3.13 改造 `app/api/v1/auth.py`：1 处 ResponseModel(code=404) → BizException(USER_NOT_FOUND)
