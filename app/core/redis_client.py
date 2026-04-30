"""
Redis 客户端模块
用于缓存层，支持登录失败计数、Token黑名单等
"""
import redis.asyncio as redis
from typing import Optional
import logging
from app.core.config import settings

logger = logging.getLogger(__name__)


class RedisClient:
    """Redis 客户端封装"""

    _instance: Optional['RedisClient'] = None
    _client: Optional[redis.Redis] = None

    def __new__(cls):
        if cls._instance is None:
            cls._instance = super().__new__(cls)
        return cls._instance

    async def connect(self) -> bool:
        """连接 Redis"""
        if not settings.REDIS_ENABLED:
            logger.info("Redis 未启用，使用内存缓存")
            return False

        try:
            self._client = redis.from_url(
                settings.REDIS_URL,
                encoding="utf-8",
                decode_responses=True
            )
            await self._client.ping()
            logger.info("Redis 连接成功")
            return True
        except Exception as e:
            logger.warning(f"Redis 连接失败: {e}，将使用内存缓存")
            self._client = None
            return False

    async def disconnect(self):
        """断开连接"""
        if self._client:
            await self._client.close()
            self._client = None

    @property
    def client(self) -> Optional[redis.Redis]:
        """获取 Redis 客户端"""
        return self._client

    def is_connected(self) -> bool:
        """检查是否已连接"""
        return self._client is not None


# 全局 Redis 客户端实例
redis_client = RedisClient()


# 内存缓存降级方案
class MemoryCache:
    """内存缓存（Redis 不可用时的降级方案）"""

    def __init__(self):
        self._data: dict = {}

    async def get(self, key: str) -> Optional[str]:
        return self._data.get(key)

    async def set(self, key: str, value: str, ex: int = None):
        self._data[key] = value
        # 注意：内存缓存不支持过期，生产环境应使用 Redis

    async def delete(self, key: str):
        self._data.pop(key, None)

    async def incr(self, key: str) -> int:
        if key not in self._data:
            self._data[key] = "0"
        value = int(self._data[key]) + 1
        self._data[key] = str(value)
        return value

    async def expire(self, key: str, seconds: int):
        # 内存缓存不支持过期
        pass


# 内存缓存实例
memory_cache = MemoryCache()


async def get_cache():
    """获取缓存客户端（Redis 或内存缓存）"""
    if redis_client.is_connected():
        return redis_client.client
    return memory_cache
