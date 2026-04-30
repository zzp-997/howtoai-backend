"""
请求频率限制中间件
基于 Flask-Limiter 实现 IP 级别和用户级别的限流
"""
from functools import wraps
from flask import request, jsonify, g
from flask_limiter import Limiter
from flask_limiter.util import get_remote_address
import logging
from typing import Optional, Callable
from app.core.config import settings
from app.core.redis_client import get_cache

logger = logging.getLogger(__name__)


class RateLimitMiddleware:
    """请求频率限制中间件"""

    _limiter: Optional[Limiter] = None

    @classmethod
    def init_app(cls, app):
        """
        初始化限流中间件

        Args:
            app: Flask 应用实例
        """
        # 配置存储后端
        if settings.REDIS_ENABLED:
            storage_uri = settings.REDIS_URL
        else:
            # 使用内存存储
            storage_uri = "memory://"

        cls._limiter = Limiter(
            app=app,
            key_func=cls._get_key,
            default_limits=[f"{settings.RATE_LIMIT_GLOBAL} per minute"],
            storage_uri=storage_uri,
            strategy="fixed-window",
            headers_enabled=True  # 在响应头中返回限流信息
        )

        # 添加自定义错误处理
        @app.errorhandler(429)
        def ratelimit_handler(e):
            return jsonify({
                "code": 429,
                "message": "请求过于频繁，请稍后再试",
                "data": {
                    "retry_after": e.description
                }
            }), 429

        logger.info("限流中间件初始化完成")

    @classmethod
    def _get_key(cls):
        """
        获取限流键
        优先使用用户ID，其次使用IP地址
        """
        # 如果用户已登录，使用用户ID
        user_id = getattr(g, 'user_id', None)
        if user_id:
            return f"user:{user_id}"

        # 否则使用IP地址
        return f"ip:{get_remote_address()}"

    @classmethod
    def limit_global(cls):
        """
        全局限流装饰器
        限制：settings.RATE_LIMIT_GLOBAL 次/分钟
        """
        if cls._limiter is None:
            raise RuntimeError("限流中间件未初始化，请先调用 init_app")

        return cls._limiter.limit(f"{settings.RATE_LIMIT_GLOBAL} per minute")

    @classmethod
    def limit_user(cls):
        """
        用户级限流装饰器
        限制：settings.RATE_LIMIT_USER 次/分钟
        """
        if cls._limiter is None:
            raise RuntimeError("限流中间件未初始化，请先调用 init_app")

        return cls._limiter.limit(f"{settings.RATE_LIMIT_USER} per minute")

    @classmethod
    def limit_login(cls):
        """
        登录接口限流装饰器
        限制：settings.RATE_LIMIT_LOGIN 次/分钟
        """
        if cls._limiter is None:
            raise RuntimeError("限流中间件未初始化，请先调用 init_app")

        # 登录接口使用IP限流
        return cls._limiter.limit(
            f"{settings.RATE_LIMIT_LOGIN} per minute",
            key_func=get_remote_address
        )

    @classmethod
    def limit_sensitive(cls):
        """
        敏感操作限流装饰器
        限制：settings.RATE_LIMIT_SENSITIVE 次/小时
        """
        if cls._limiter is None:
            raise RuntimeError("限流中间件未初始化，请先调用 init_app")

        return cls._limiter.limit(f"{settings.RATE_LIMIT_SENSITIVE} per hour")

    @classmethod
    def custom_limit(cls, limit_string: str, key_func: Optional[Callable] = None):
        """
        自定义限流装饰器

        Args:
            limit_string: 限流字符串，如 "10 per minute"
            key_func: 自定义键函数
        """
        if cls._limiter is None:
            raise RuntimeError("限流中间件未初始化，请先调用 init_app")

        if key_func:
            return cls._limiter.limit(limit_string, key_func=key_func)
        return cls._limiter.limit(limit_string)


def rate_limit_login(f):
    """
    登录接口限流装饰器（便捷方法）
    """
    @wraps(f)
    def decorated_function(*args, **kwargs):
        return RateLimitMiddleware.limit_login()(f)(*args, **kwargs)
    return decorated_function


def rate_limit_sensitive(f):
    """
    敏感操作限流装饰器（便捷方法）
    """
    @wraps(f)
    def decorated_function(*args, **kwargs):
        return RateLimitMiddleware.limit_sensitive()(f)(*args, **kwargs)
    return decorated_function
