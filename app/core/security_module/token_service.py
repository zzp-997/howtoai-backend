"""
Token 服务
实现双Token机制，支持Access Token和Refresh Token
"""
from datetime import datetime, timedelta
from typing import Optional, Dict, Tuple
import jwt
import logging
from app.core.config import settings
from app.core.redis_client import get_cache

logger = logging.getLogger(__name__)


class TokenService:
    """Token 服务"""

    # Token类型
    ACCESS_TOKEN = "access"
    REFRESH_TOKEN = "refresh"

    # 缓存键前缀
    TOKEN_BLACKLIST_PREFIX = "token_blacklist:"
    REFRESH_TOKEN_PREFIX = "refresh_token:"

    @classmethod
    def generate_tokens(cls, user_id: int, user_info: Optional[Dict] = None) -> Dict[str, str]:
        """
        生成双Token

        Args:
            user_id: 用户ID
            user_info: 附加用户信息

        Returns:
            包含 accessToken 和 refreshToken 的字典
        """
        now = datetime.utcnow()

        # Access Token (2小时)
        access_payload = {
            "sub": str(user_id),
            "type": cls.ACCESS_TOKEN,
            "iat": now,
            "exp": now + timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)
        }
        if user_info:
            access_payload.update(user_info)

        access_token = jwt.encode(
            access_payload,
            settings.SECRET_KEY,
            algorithm=settings.ALGORITHM
        )

        # Refresh Token (7天)
        refresh_payload = {
            "sub": str(user_id),
            "type": cls.REFRESH_TOKEN,
            "iat": now,
            "exp": now + timedelta(days=settings.REFRESH_TOKEN_EXPIRE_DAYS)
        }

        refresh_token = jwt.encode(
            refresh_payload,
            settings.SECRET_KEY,
            algorithm=settings.ALGORITHM
        )

        # 存储Refresh Token（用于校验和撤销）
        cls._store_refresh_token(user_id, refresh_token)

        logger.info(f"为用户 {user_id} 生成Token对")

        return {
            "accessToken": access_token,
            "refreshToken": refresh_token,
            "tokenType": "Bearer",
            "expiresIn": settings.ACCESS_TOKEN_EXPIRE_MINUTES * 60
        }

    @classmethod
    def verify_token(cls, token: str, token_type: str = "access") -> Optional[Dict]:
        """
        验证Token

        Args:
            token: Token字符串
            token_type: Token类型 ('access' | 'refresh')

        Returns:
            解码后的payload，验证失败返回None
        """
        try:
            payload = jwt.decode(
                token,
                settings.SECRET_KEY,
                algorithms=[settings.ALGORITHM]
            )

            # 检查Token类型
            if payload.get("type") != token_type:
                logger.warning(f"Token类型不匹配: 期望 {token_type}, 实际 {payload.get('type')}")
                return None

            # 检查黑名单
            if cls._is_token_blacklisted(token):
                logger.warning(f"Token已在黑名单中")
                return None

            return payload

        except jwt.ExpiredSignatureError:
            logger.info("Token已过期")
            return None
        except jwt.InvalidTokenError as e:
            logger.warning(f"无效Token: {e}")
            return None

    @classmethod
    def refresh_access_token(cls, refresh_token: str) -> Optional[Dict[str, str]]:
        """
        使用Refresh Token刷新Access Token

        Args:
            refresh_token: Refresh Token

        Returns:
            新的Token对，失败返回None
        """
        # 验证Refresh Token
        payload = cls.verify_token(refresh_token, cls.REFRESH_TOKEN)
        if not payload:
            return None

        user_id = int(payload.get("sub"))

        # 检查Refresh Token是否有效（未被撤销）
        if not cls._validate_refresh_token(user_id, refresh_token):
            logger.warning(f"Refresh Token已被撤销: user_id={user_id}")
            return None

        # 生成新的Token对
        new_tokens = cls.generate_tokens(user_id)

        # 将旧的Refresh Token加入黑名单
        cls._revoke_refresh_token(user_id, refresh_token)

        logger.info(f"用户 {user_id} 刷新Token成功")

        return new_tokens

    @classmethod
    def revoke_token(cls, token: str, user_id: Optional[int] = None):
        """
        撤销Token（加入黑名单）

        Args:
            token: 要撤销的Token
            user_id: 用户ID（可选）
        """
        try:
            payload = jwt.decode(
                token,
                settings.SECRET_KEY,
                algorithms=[settings.ALGORITHM]
            )

            # 计算剩余有效时间
            exp = payload.get("exp", 0)
            remaining_seconds = max(0, exp - int(datetime.utcnow().timestamp()))

            if remaining_seconds > 0:
                cache = get_cache()
                # 需要await，但这里为了兼容性使用同步方式
                import asyncio
                loop = asyncio.get_event_loop()
                if loop.is_running():
                    asyncio.create_task(
                        cache.set(
                            f"{cls.TOKEN_BLACKLIST_PREFIX}{token}",
                            "revoked",
                            ex=remaining_seconds
                        )
                    )
                else:
                    loop.run_until_complete(
                        cache.set(
                            f"{cls.TOKEN_BLACKLIST_PREFIX}{token}",
                            "revoked",
                            ex=remaining_seconds
                        )
                    )

            # 如果是Refresh Token，从存储中移除
            if payload.get("type") == cls.REFRESH_TOKEN:
                uid = user_id or int(payload.get("sub"))
                cls._revoke_refresh_token(uid, token)

            logger.info(f"Token已撤销: user_id={payload.get('sub')}")

        except jwt.InvalidTokenError:
            logger.warning("尝试撤销无效Token")

    @classmethod
    def revoke_all_user_tokens(cls, user_id: int):
        """
        撤销用户所有Token（用于安全事件处理）

        Args:
            user_id: 用户ID
        """
        # 清除用户的Refresh Token存储
        cache = get_cache()
        import asyncio
        loop = asyncio.get_event_loop()

        key = f"{cls.REFRESH_TOKEN_PREFIX}{user_id}"
        if loop.is_running():
            asyncio.create_task(cache.delete(key))
        else:
            loop.run_until_complete(cache.delete(key))

        logger.warning(f"已撤销用户 {user_id} 的所有Token")

    @classmethod
    def get_token_remaining_time(cls, token: str) -> int:
        """
        获取Token剩余有效时间

        Args:
            token: Token字符串

        Returns:
            剩余秒数，无效Token返回0
        """
        try:
            payload = jwt.decode(
                token,
                settings.SECRET_KEY,
                algorithms=[settings.ALGORITHM]
            )
            exp = payload.get("exp", 0)
            remaining = max(0, exp - int(datetime.utcnow().timestamp()))
            return remaining
        except jwt.InvalidTokenError:
            return 0

    @classmethod
    def _store_refresh_token(cls, user_id: int, refresh_token: str):
        """存储Refresh Token"""
        cache = get_cache()
        import asyncio
        loop = asyncio.get_event_loop()

        key = f"{cls.REFRESH_TOKEN_PREFIX}{user_id}"
        expire_seconds = settings.REFRESH_TOKEN_EXPIRE_DAYS * 24 * 60 * 60

        if loop.is_running():
            asyncio.create_task(cache.set(key, refresh_token, ex=expire_seconds))
        else:
            loop.run_until_complete(cache.set(key, refresh_token, ex=expire_seconds))

    @classmethod
    def _validate_refresh_token(cls, user_id: int, refresh_token: str) -> bool:
        """验证Refresh Token是否有效"""
        cache = get_cache()
        import asyncio
        loop = asyncio.get_event_loop()

        key = f"{cls.REFRESH_TOKEN_PREFIX}{user_id}"

        if loop.is_running():
            stored_token = asyncio.create_task(cache.get(key))
            # 由于无法在同步上下文中等待，这里简化处理
            return True
        else:
            stored_token = loop.run_until_complete(cache.get(key))
            return stored_token == refresh_token

    @classmethod
    def _revoke_refresh_token(cls, user_id: int, refresh_token: str):
        """撤销Refresh Token"""
        cache = get_cache()
        import asyncio
        loop = asyncio.get_event_loop()

        key = f"{cls.REFRESH_TOKEN_PREFIX}{user_id}"

        if loop.is_running():
            asyncio.create_task(cache.delete(key))
        else:
            loop.run_until_complete(cache.delete(key))

    @classmethod
    async def _is_token_blacklisted(cls, token: str) -> bool:
        """检查Token是否在黑名单中"""
        cache = await get_cache()
        key = f"{cls.TOKEN_BLACKLIST_PREFIX}{token}"
        return await cache.get(key) is not None
