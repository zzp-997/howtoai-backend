"""
FastAPI 请求频率限制中间件
基于 slowapi 实现 IP 级别和用户级别的限流
"""
from fastapi import FastAPI, Request, Response, HTTPException
from fastapi.responses import JSONResponse
from slowapi import Limiter, _rate_limit_exceeded_handler
from slowapi.util import get_remote_address
from slowapi.errors import RateLimitExceeded
from slowapi.middleware import SlowAPIMiddleware
import logging
from typing import Optional, Callable
from app.core.config import settings

logger = logging.getLogger(__name__)


class RateLimitMiddleware:
    """FastAPI 请求频率限制中间件"""

    _limiter: Optional[Limiter] = None
    _app: Optional[FastAPI] = None

    @classmethod
    def init_app(cls, app: FastAPI):
        """
        初始化限流中间件

        Args:
            app: FastAPI 应用实例
        """
        cls._app = app

        # 配置存储后端
        if settings.REDIS_ENABLED:
            storage_uri = settings.REDIS_URL
        else:
            # 使用内存存储
            storage_uri = "memory://"

        cls._limiter = Limiter(
            key_func=cls._get_key,
            default_limits=[f"{settings.RATE_LIMIT_GLOBAL} per minute"],
            storage_uri=storage_uri,
            headers_enabled=True
        )

        # 设置状态
        app.state.limiter = cls._limiter

        # 添加异常处理器
        app.add_exception_handler(RateLimitExceeded, cls._rate_limit_exceeded_handler)

        # 添加中间件
        app.add_middleware(SlowAPIMiddleware)

        logger.info(f"限流中间件初始化完成: 全局限制={settings.RATE_LIMIT_GLOBAL}次/分钟")

    @classmethod
    def _get_key(cls, request: Request) -> str:
        """
        获取限流键
        优先使用用户ID，其次使用IP地址
        """
        # 如果用户已登录，使用用户ID
        user_id = getattr(request.state, 'user_id', None)
        if user_id:
            return f"user:{user_id}"

        # 否则使用IP地址
        return f"ip:{get_remote_address(request)}"

    @classmethod
    async def _rate_limit_exceeded_handler(cls, request: Request, exc: RateLimitExceeded):
        """自定义429错误处理"""
        return JSONResponse(
            status_code=429,
            content={
                "code": 429,
                "message": "请求过于频繁，请稍后再试",
                "data": {
                    "retry_after": str(exc.detail)
                }
            }
        )

    @classmethod
    def get_limiter(cls) -> Limiter:
        """获取限流器实例"""
        if cls._limiter is None:
            raise RuntimeError("限流中间件未初始化，请先调用 init_app")
        return cls._limiter

    @classmethod
    def limit_global(cls) -> Callable:
        """全局限流装饰器"""
        return cls.get_limiter().limit(f"{settings.RATE_LIMIT_GLOBAL} per minute")

    @classmethod
    def limit_user(cls) -> Callable:
        """用户级限流装饰器"""
        return cls.get_limiter().limit(f"{settings.RATE_LIMIT_USER} per minute")

    @classmethod
    def limit_login(cls) -> Callable:
        """登录接口限流装饰器"""
        return cls.get_limiter().limit(
            f"{settings.RATE_LIMIT_LOGIN} per minute",
            key_func=get_remote_address
        )

    @classmethod
    def limit_sensitive(cls) -> Callable:
        """敏感操作限流装饰器"""
        return cls.get_limiter().limit(f"{settings.RATE_LIMIT_SENSITIVE} per hour")


# 便捷装饰器函数
def rate_limit_login():
    """登录接口限流"""
    return RateLimitMiddleware.limit_login()

def rate_limit_sensitive():
    """敏感操作限流"""
    return RateLimitMiddleware.limit_sensitive()