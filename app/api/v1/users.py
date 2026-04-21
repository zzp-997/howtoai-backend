"""
用户管理 API
"""
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from typing import List
from app.core.database import get_db
from app.schemas.user import UserResponse, UserUpdate
from app.schemas.common import ResponseModel
from app.services.auth_service import auth_service
from app.api.v1.auth import get_current_user
from app.models import User
from sqlalchemy import select

router = APIRouter(prefix="/users", tags=["用户管理"])


@router.get("", response_model=ResponseModel[List[UserResponse]])
async def get_users(
    db: AsyncSession = Depends(get_db),
    current_user: UserResponse = Depends(get_current_user)
):
    """获取用户列表（管理员）"""
    if current_user.role != "admin":
        raise HTTPException(status_code=403, detail="无权限")

    result = await db.execute(select(User).where(User.is_active == True))
    users = result.scalars().all()
    return ResponseModel(data=[UserResponse.model_validate(u) for u in users])


@router.get("/{user_id}", response_model=ResponseModel[UserResponse])
async def get_user(
    user_id: int,
    db: AsyncSession = Depends(get_db),
    current_user: UserResponse = Depends(get_current_user)
):
    """获取用户详情"""
    if current_user.role != "admin" and current_user.id != user_id:
        raise HTTPException(status_code=403, detail="无权限")

    user = await auth_service.get_by_id(db, user_id)
    if not user:
        raise HTTPException(status_code=404, detail="用户不存在")
    return ResponseModel(data=UserResponse.model_validate(user))


@router.put("/{user_id}", response_model=ResponseModel[UserResponse])
async def update_user(
    user_id: int,
    data: UserUpdate,
    db: AsyncSession = Depends(get_db),
    current_user: UserResponse = Depends(get_current_user)
):
    """更新用户信息"""
    if current_user.role != "admin" and current_user.id != user_id:
        raise HTTPException(status_code=403, detail="无权限")

    user = await auth_service.get_by_id(db, user_id)
    if not user:
        raise HTTPException(status_code=404, detail="用户不存在")

    # 更新字段
    update_data = data.model_dump(exclude_unset=True, by_alias=False)
    for key, value in update_data.items():
        setattr(user, key, value)

    await db.commit()
    await db.refresh(user)
    return ResponseModel(data=UserResponse.model_validate(user), message="更新成功")
