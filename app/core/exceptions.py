"""
统一业务异常

所有业务异常统一抛出 BizException，由全局异常处理器统一响应。
不再使用 HTTPException 返回业务错误。

注意：FastAPI 依赖注入链中的认证拦截（如 get_current_user 中的 401）
仍使用 HTTPException，因为 Depends 机制依赖 HTTP 状态码。
"""
from app.core.error_codes import ErrorCode, ERROR_MESSAGES


class BizException(Exception):
    """业务异常 — 前端可感知的业务错误"""

    def __init__(self, code: ErrorCode, message: str = None):
        self.code = code
        self.message = message or ERROR_MESSAGES.get(code, "操作失败")
        super().__init__(self.message)
