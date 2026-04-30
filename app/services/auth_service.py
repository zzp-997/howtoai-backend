"""
认证服务 - 集成安全模块
"""
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from app.models import User
from app.schemas.user import UserCreate, UserResponse
from app.core.security import verify_password, get_password_hash, create_access_token
from app.core.security_module.login_limit_service import LoginLimitService
from app.core.security_module.token_service import TokenService
from app.core.security_module.password_service import PasswordService
from app.core.security_module.audit_service import AuditService
from typing import Optional, Dict
import logging

logger = logging.getLogger(__name__)


class AuthService:
    """认证服务类"""

    async def get_by_username(self, db: AsyncSession, username: str) -> Optional[User]:
        """根据用户名查询用户"""
        result = await db.execute(select(User).where(User.username == username))
        return result.scalar_one_or_none()

    async def get_by_id(self, db: AsyncSession, user_id: int) -> Optional[User]:
        """根据ID查询用户"""
        result = await db.execute(select(User).where(User.id == user_id))
        return result.scalar_one_or_none()

    async def authenticate(self, db: AsyncSession, username: str, password: str) -> Optional[User]:
        """认证用户"""
        user = await self.get_by_username(db, username)
        if not user:
            return None
        if not verify_password(password, user.password):
            return None
        return user

    async def login(self, db: AsyncSession, username: str, password: str, ip_address: str = None) -> dict:
        """
        登录 - 集成安全模块

        Args:
            db: 数据库会话
            username: 用户名
            password: 密码
            ip_address: 客户端IP

        Returns:
            登录结果，包含token、用户信息、锁定状态等
        """
        # 1. 查询用户
        user = await self.get_by_username(db, username)

        if not user:
            # 用户不存在，仍记录失败日志（但不暴露具体原因）
            await AuditService.log_login(0, "failed", ip_address, "用户不存在")
            return {
                "success": False,
                "message": "用户名或密码错误",
                "locked": False
            }

        user_id = user.id

        # 2. 检查账户锁定状态
        is_locked, remaining_seconds = await LoginLimitService.check_account_locked(user_id)
        if is_locked:
            return {
                "success": False,
                "message": f"账户已锁定，请 {remaining_seconds // 60} 分钟后重试",
                "locked": True,
                "remaining_seconds": remaining_seconds
            }

        # 3. 验证密码
        if not verify_password(password, user.password):
            # 记录登录失败
            fail_result = await LoginLimitService.record_login_failure(user_id, ip_address)
            await AuditService.log_login(user_id, "failed", ip_address, "密码错误")

            return {
                "success": False,
                "message": fail_result["message"],
                "locked": fail_result["locked"],
                "remaining_attempts": fail_result["remaining_attempts"],
                "remaining_seconds": fail_result["remaining_seconds"]
            }

        # 4. 登录成功 - 清除失败计数
        await LoginLimitService.record_login_success(user_id)
        await AuditService.log_login(user_id, "success", ip_address)

        # 5. 检查密码过期状态
        password_changed_at = getattr(user, 'password_changed_at', None)
        expiry_status = PasswordService.check_password_expiry(password_changed_at)

        # 6. 生成双Token
        token_result = TokenService.generate_tokens(user_id, {
            "username": user.username,
            "role": user.role
        })

        logger.info(f"用户 {user_id} 登录成功")

        return {
            "success": True,
            "message": "登录成功",
            "data": {
                "accessToken": token_result["accessToken"],
                "refreshToken": token_result["refreshToken"],
                "tokenType": token_result["tokenType"],
                "expiresIn": token_result["expiresIn"],
                "user": UserResponse.model_validate(user),
                "passwordExpiry": expiry_status if expiry_status["expiring_soon"] else None
            }
        }

    async def refresh_token(self, refresh_token: str) -> Optional[Dict]:
        """
        刷新Token

        Args:
            refresh_token: Refresh Token

        Returns:
            新的Token对
        """
        new_tokens = TokenService.refresh_access_token(refresh_token)
        if new_tokens:
            return {
                "success": True,
                "data": new_tokens
            }
        return {
            "success": False,
            "message": "Refresh Token无效或已过期"
        }

    async def logout(self, token: str, refresh_token: Optional[str] = None, user_id: int = None):
        """
        登出 - 撤销Token

        Args:
            token: Access Token
            refresh_token: Refresh Token（可选）
            user_id: 用户ID
        """
        TokenService.revoke_token(token, user_id)
        if refresh_token:
            TokenService.revoke_token(refresh_token, user_id)

        await AuditService.log_operation("logout", user_id=user_id)

        logger.info(f"用户 {user_id} 登出成功")

    async def change_password(self, db: AsyncSession, user_id: int,
                               old_password: str, new_password: str) -> Dict:
        """
        修改密码

        Args:
            db: 数据库会话
            user_id: 用户ID
            old_password: 旧密码
            new_password: 新密码

        Returns:
            修改结果
        """
        user = await self.get_by_id(db, user_id)
        if not user:
            return {"success": False, "message": "用户不存在"}

        # 验证旧密码
        if not verify_password(old_password, user.password):
            return {"success": False, "message": "旧密码错误"}

        # 验证新密码强度
        validation = PasswordService.validate_password(new_password, {
            "username": user.username,
            "email": user.email
        })
        if not validation["valid"]:
            return {
                "success": False,
                "message": "新密码不符合安全要求",
                "errors": validation["errors"],
                "strength": validation["strength"]
            }

        # 检查历史密码
        password_history = getattr(user, 'password_history', None)
        if not PasswordService.check_password_history(new_password, password_history, user_id):
            return {"success": False, "message": "新密码不能与最近5次密码相同"}

        # 更新密码
        hashed_password = get_password_hash(new_password)
        user.password = hashed_password
        user.password_changed_at = datetime.utcnow()
        user.password_history = PasswordService.update_password_history(password_history, new_password)

        await db.commit()

        # 撤销所有Token（强制重新登录）
        TokenService.revoke_all_user_tokens(user_id)

        await AuditService.log_operation("password_change", user_id=user_id)

        logger.info(f"用户 {user_id} 修改密码成功")

        return {
            "success": True,
            "message": "密码修改成功，请重新登录"
        }

    async def create_user(self, db: AsyncSession, user_data: UserCreate) -> User:
        """创建用户"""
        # 检查用户名是否存在
        existing = await self.get_by_username(db, user_data.username)
        if existing:
            raise ValueError("用户名已存在")

        # 验证密码强度
        validation = PasswordService.validate_password(user_data.password)
        if not validation["valid"]:
            raise ValueError(f"密码不符合安全要求: {', '.join(validation['errors'])}")

        # 创建用户
        hashed_password = get_password_hash(user_data.password)
        user = User(
            username=user_data.username,
            password=hashed_password,
            name=user_data.name,
            role=user_data.role,
            department=user_data.department,
            position=user_data.position,
            phone=user_data.phone,
            email=user_data.email,
            password_changed_at=datetime.utcnow()
        )
        db.add(user)
        await db.commit()
        await db.refresh(user)
        return user


# 全局服务实例
auth_service = AuthService()
