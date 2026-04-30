"""
登录失败限制服务
防止暴力破解攻击，连续登录失败后锁定账户
"""
from datetime import datetime, timedelta
from typing import Optional, Tuple
import logging
from app.core.config import settings
from app.core.redis_client import get_cache

logger = logging.getLogger(__name__)


class LoginLimitService:
    """登录失败限制服务"""

    # 缓存键前缀
    FAIL_COUNT_PREFIX = "login_fail:"
    LOCK_PREFIX = "login_lock:"

    @classmethod
    async def check_account_locked(cls, user_id: int) -> Tuple[bool, Optional[int]]:
        """
        检查账户是否被锁定

        Args:
            user_id: 用户ID

        Returns:
            (是否锁定, 剩余锁定秒数)
        """
        cache = await get_cache()
        lock_key = f"{cls.LOCK_PREFIX}{user_id}"

        # 检查是否有锁定记录
        lock_until = await cache.get(lock_key)
        if lock_until:
            lock_time = datetime.fromisoformat(lock_until)
            now = datetime.now()

            if now < lock_time:
                remaining_seconds = int((lock_time - now).total_seconds())
                return True, remaining_seconds
            else:
                # 锁定已过期，清除锁定状态
                await cache.delete(lock_key)
                await cache.delete(f"{cls.FAIL_COUNT_PREFIX}{user_id}")

        return False, None

    @classmethod
    async def record_login_failure(cls, user_id: int, ip_address: str, reason: str = "密码错误") -> dict:
        """
        记录登录失败

        Args:
            user_id: 用户ID
            ip_address: 客户端IP
            reason: 失败原因

        Returns:
            包含剩余尝试次数、是否锁定等信息的字典
        """
        cache = await get_cache()
        fail_key = f"{cls.FAIL_COUNT_PREFIX}{user_id}"
        lock_key = f"{cls.LOCK_PREFIX}{user_id}"

        # 检查是否已锁定
        is_locked, remaining = await cls.check_account_locked(user_id)
        if is_locked:
            return {
                "locked": True,
                "remaining_seconds": remaining,
                "remaining_attempts": 0,
                "message": f"账户已锁定，请 {remaining} 秒后重试"
            }

        # 增加失败计数
        fail_count = await cache.incr(fail_key)

        # 设置失败计数过期时间（滑动窗口）
        if fail_count == 1:
            window_seconds = settings.LOGIN_FAIL_WINDOW_MINUTES * 60
            await cache.expire(fail_key, window_seconds)

        remaining_attempts = settings.LOGIN_FAIL_THRESHOLD - fail_count

        # 判断是否需要锁定
        if fail_count >= settings.LOGIN_FAIL_THRESHOLD:
            # 锁定账户
            lock_duration = settings.LOGIN_LOCK_DURATION_MINUTES
            lock_until = datetime.now() + timedelta(minutes=lock_duration)
            await cache.set(lock_key, lock_until.isoformat(), ex=lock_duration * 60)

            logger.warning(f"用户 {user_id} 登录失败次数达到阈值，已锁定 {lock_duration} 分钟")

            return {
                "locked": True,
                "remaining_seconds": lock_duration * 60,
                "remaining_attempts": 0,
                "message": f"账户已锁定，请 {lock_duration} 分钟后重试"
            }

        logger.info(f"用户 {user_id} 登录失败，剩余尝试次数: {remaining_attempts}")

        return {
            "locked": False,
            "remaining_attempts": remaining_attempts,
            "remaining_seconds": None,
            "message": f"用户名或密码错误，还剩 {remaining_attempts} 次尝试机会"
        }

    @classmethod
    async def record_login_success(cls, user_id: int):
        """
        记录登录成功，清除失败计数

        Args:
            user_id: 用户ID
        """
        cache = await get_cache()
        fail_key = f"{cls.FAIL_COUNT_PREFIX}{user_id}"
        lock_key = f"{cls.LOCK_PREFIX}{user_id}"

        # 清除失败计数和锁定状态
        await cache.delete(fail_key)
        await cache.delete(lock_key)

        logger.info(f"用户 {user_id} 登录成功，已清除失败计数")

    @classmethod
    async def admin_unlock(cls, user_id: int) -> bool:
        """
        管理员手动解锁账户

        Args:
            user_id: 用户ID

        Returns:
            是否解锁成功
        """
        cache = await get_cache()
        fail_key = f"{cls.FAIL_COUNT_PREFIX}{user_id}"
        lock_key = f"{cls.LOCK_PREFIX}{user_id}"

        await cache.delete(fail_key)
        await cache.delete(lock_key)

        logger.info(f"管理员解锁用户 {user_id} 账户")
        return True

    @classmethod
    async def get_lock_status(cls, user_id: int) -> dict:
        """
        获取账户锁定状态详情

        Args:
            user_id: 用户ID

        Returns:
            锁定状态详情
        """
        cache = await get_cache()
        fail_key = f"{cls.FAIL_COUNT_PREFIX}{user_id}"
        lock_key = f"{cls.LOCK_PREFIX}{user_id}"

        fail_count = await cache.get(fail_key)
        lock_until = await cache.get(lock_key)

        is_locked, remaining_seconds = await cls.check_account_locked(user_id)

        return {
            "is_locked": is_locked,
            "fail_count": int(fail_count) if fail_count else 0,
            "lock_until": lock_until,
            "remaining_seconds": remaining_seconds,
            "threshold": settings.LOGIN_FAIL_THRESHOLD
        }
