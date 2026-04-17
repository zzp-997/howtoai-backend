"""
认证 API
"""
from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from sqlalchemy.ext.asyncio import AsyncSession
from app.core.database import get_db
from app.core.security import decode_access_token
from app.schemas.user import LoginRequest, LoginResponse, UserResponse
from app.schemas.common import ResponseModel
from app.services.auth_service import auth_service
from typing import Optional

router = APIRouter(prefix="/auth", tags=["认证"])
security = HTTPBearer()


async def get_current_user(
    credentials: HTTPAuthorizationCredentials = Depends(security),
    db: AsyncSession = Depends(get_db)
) -> UserResponse:
    """获取当前用户"""
    token = credentials.credentials
    payload = decode_access_token(token)
    if not payload:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="无效的认证令牌"
        )

    user_id = payload.get("userId")
    user = await auth_service.get_by_id(db, user_id)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="用户不存在"
        )

    return UserResponse.model_validate(user)


@router.post("/login")
async def login(request: LoginRequest, db: AsyncSession = Depends(get_db)):
    """用户登录"""
    result = await auth_service.login(db, request.username, request.password)
    if not result:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="用户名或密码错误"
        )
    return ResponseModel(code=200, message="登录成功", data=result)


@router.post("/logout")
async def logout():
    """用户登出"""
    return ResponseModel(code=200, message="登出成功", data=None)


@router.get("/me")
async def get_me(current_user: UserResponse = Depends(get_current_user)):
    """获取当前用户信息"""
    return ResponseModel(code=200, message="success", data=current_user)