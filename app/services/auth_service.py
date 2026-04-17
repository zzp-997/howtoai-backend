"""
认证服务
"""
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from app.models import User
from app.schemas.user import UserCreate, UserResponse
from app.core.security import verify_password, get_password_hash, create_access_token
from typing import Optional


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

    async def login(self, db: AsyncSession, username: str, password: str) -> dict:
        """登录"""
        user = await self.authenticate(db, username, password)
        if not user:
            return None

        # 创建 token
        token = create_access_token({
            "userId": user.id,
            "username": user.username,
            "role": user.role
        })

        return {
            "token": token,
            "user": UserResponse.model_validate(user)
        }

    async def create_user(self, db: AsyncSession, user_data: UserCreate) -> User:
        """创建用户"""
        # 检查用户名是否存在
        existing = await self.get_by_username(db, user_data.username)
        if existing:
            raise ValueError("用户名已存在")

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
            email=user_data.email
        )
        db.add(user)
        await db.commit()
        await db.refresh(user)
        return user


# 全局服务实例
auth_service = AuthService()