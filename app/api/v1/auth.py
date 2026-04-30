"""
认证 API - 集成安全模块
"""
from fastapi import APIRouter, Depends, HTTPException, status, Request
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from sqlalchemy.ext.asyncio import AsyncSession
from app.core.database import get_db
from app.core.security import decode_access_token
from app.core.security_module.rate_limit_middleware_fastapi import rate_limit_login, rate_limit_sensitive
from app.schemas.user import LoginRequest, UserResponse
from app.schemas.security import (
    PasswordChangeRequest, PasswordStrengthResponse,
    TokenRefreshRequest, TokenRefreshResponse,
    PasswordExpiryStatus, PasswordSuggestions
)
from app.schemas.common import ResponseModel
from app.services.auth_service import auth_service
from app.core.security_module.password_service import PasswordService
from app.core.security_module.token_service import TokenService
from app.core.security_module.audit_service import AuditService
from typing import Optional
import logging

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/auth", tags=["认证"])
security = HTTPBearer()


async def get_client_ip(request: Request) -> str:
    """获取客户端真实IP"""
    forwarded = request.headers.get("X-Forwarded-For")
    if forwarded:
        return forwarded.split(",")[0].strip()
    real_ip = request.headers.get("X-Real-IP")
    if real_ip:
        return real_ip
    return request.client.host or "unknown"


async def get_current_user(
    request: Request,
    credentials: HTTPAuthorizationCredentials = Depends(security),
    db: AsyncSession = Depends(get_db)
) -> UserResponse:
    """获取当前用户"""
    token = credentials.credentials

    # 验证Token（包括黑名单检查）
    payload = TokenService.verify_token(token, "access")
    if not payload:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="无效的认证令牌"
        )

    user_id = payload.get("sub")
    user = await auth_service.get_by_id(db, int(user_id))
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="用户不存在"
        )

    # 存储用户ID到请求状态（用于限流）
    request.state.user_id = user.id

    return UserResponse.model_validate(user)


@router.post("/login")
@rate_limit_login()
async def login(
    request: Request,
    login_request: LoginRequest,
    db: AsyncSession = Depends(get_db)
):
    """
    用户登录

    集成安全功能：
    - 登录失败限制（连续5次失败锁定15分钟）
    - 登录日志记录
    - 双Token机制
    """
    ip_address = await get_client_ip(request)

    result = await auth_service.login(
        db,
        login_request.username,
        login_request.password,
        ip_address
    )

    if not result.get("success"):
        # 返回详细的错误信息（包含锁定状态）
        return ResponseModel(
            code=401,
            message=result.get("message"),
            data={
                "locked": result.get("locked", False),
                "remainingAttempts": result.get("remaining_attempts"),
                "remainingSeconds": result.get("remaining_seconds")
            }
        )

    return ResponseModel(
        code=200,
        message="登录成功",
        data=result.get("data")
    )


@router.post("/logout")
async def logout(
    request: Request,
    credentials: HTTPAuthorizationCredentials = Depends(security),
    db: AsyncSession = Depends(get_db)
):
    """
    用户登出

    安全功能：
    - Token撤销（加入黑名单）
    - 登出日志记录
    """
    token = credentials.credentials
    payload = decode_access_token(token)
    user_id = int(payload.get("user_id", 0)) if payload else None

    # 获取refresh_token（从请求体或头部）
    # 这里简化处理，仅撤销access_token

    await auth_service.logout(token, None, user_id)

    return ResponseModel(code=200, message="登出成功", data=None)


@router.post("/refresh")
async def refresh_token(
    request: TokenRefreshRequest,
    db: AsyncSession = Depends(get_db)
):
    """
    Token刷新

    使用Refresh Token获取新的Access Token
    """
    result = await auth_service.refresh_token(request.refresh_token)

    if not result.get("success"):
        return ResponseModel(
            code=401,
            message=result.get("message"),
            data=None
        )

    return ResponseModel(
        code=200,
        message="Token刷新成功",
        data=result.get("data")
    )


@router.get("/me")
async def get_me(current_user: UserResponse = Depends(get_current_user)):
    """获取当前用户信息"""
    return ResponseModel(code=200, message="success", data=current_user)


@router.post("/password/change")
@rate_limit_sensitive()
async def change_password(
    request: Request,
    password_request: PasswordChangeRequest,
    current_user: UserResponse = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """
    修改密码

    安全功能：
    - 密码强度校验
    - 历史密码检查
    - 密码过期时间更新
    - Token撤销（强制重新登录）
    """
    result = await auth_service.change_password(
        db,
        current_user.id,
        password_request.old_password,
        password_request.new_password
    )

    if not result.get("success"):
        return ResponseModel(
            code=400,
            message=result.get("message"),
            data={
                "errors": result.get("errors"),
                "strength": result.get("strength")
            }
        )

    return ResponseModel(
        code=200,
        message=result.get("message"),
        data={"requireRelogin": True}
    )


@router.post("/password/validate")
async def validate_password_strength(password_request: PasswordChangeRequest):
    """
    验证密码强度（用于前端实时校验）

    不需要登录，用于注册或修改密码前的预校验
    """
    validation = PasswordService.validate_password(password_request.new_password)
    strength, score = PasswordService.get_password_strength(password_request.new_password)

    return ResponseModel(
        code=200,
        message="验证完成",
        data={
            "valid": validation["valid"],
            "strength": strength,
            "score": score,
            "errors": validation["errors"],
            "warnings": validation["warnings"]
        }
    )


@router.get("/password/expiry")
async def get_password_expiry_status(
    current_user: UserResponse = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """
    获取密码过期状态

    返回密码是否过期、剩余天数等信息
    """
    user = await auth_service.get_by_id(db, current_user.id)
    if not user:
        return ResponseModel(code=404, message="用户不存在", data=None)

    password_changed_at = getattr(user, 'password_changed_at', None)
    expiry_status = PasswordService.check_password_expiry(password_changed_at)

    return ResponseModel(
        code=200,
        message="success",
        data=expiry_status
    )


@router.get("/password/suggestions")
async def get_password_suggestions():
    """
    获取密码建议

    用于指导用户创建安全密码
    """
    suggestions = PasswordService.generate_password_suggestions()

    return ResponseModel(
        code=200,
        message="success",
        data={"suggestions": suggestions}
    )


@router.get("/logs/login")
async def get_login_logs(
    page: int = 1,
    page_size: int = 20,
    current_user: UserResponse = Depends(get_current_user)
):
    """
    查询登录日志

    管理员可查询所有用户日志，普通用户仅能查看自己的
    """
    # 权限检查（管理员可查看所有）
    user_id = None if current_user.role == "admin" else current_user.id

    logs = await AuditService.query_login_logs(
        user_id=user_id,
        page=page,
        page_size=page_size
    )

    return ResponseModel(
        code=200,
        message="success",
        data=logs
    )


@router.get("/logs/operation")
async def get_operation_logs(
    page: int = 1,
    page_size: int = 20,
    current_user: UserResponse = Depends(get_current_user)
):
    """
    查询操作日志

    普通用户仅能查看自己的操作日志
    """
    logs = await AuditService.query_user_logs(
        user_id=current_user.id,
        page=page,
        page_size=page_size
    )

    return ResponseModel(
        code=200,
        message="success",
        data=logs
    )