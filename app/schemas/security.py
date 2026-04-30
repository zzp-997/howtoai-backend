"""
安全模块相关 Schema
"""
from pydantic import BaseModel, Field
from typing import Optional, List
from datetime import datetime
from app.schemas.common import CamelModel


class PasswordStrengthResponse(CamelModel):
    """密码强度响应"""
    valid: bool
    strength: str
    score: int
    errors: List[str] = []
    warnings: List[str] = []
    checks: dict = {}


class PasswordChangeRequest(BaseModel):
    """密码修改请求"""
    old_password: str = Field(..., min_length=1)
    new_password: str = Field(..., min_length=8)


class TokenRefreshRequest(BaseModel):
    """Token刷新请求"""
    refresh_token: str


class TokenRefreshResponse(CamelModel):
    """Token刷新响应"""
    access_token: str
    refresh_token: str
    token_type: str = "Bearer"
    expires_in: int


class AccountLockStatus(CamelModel):
    """账户锁定状态"""
    is_locked: bool
    fail_count: int
    lock_until: Optional[datetime] = None
    remaining_seconds: Optional[int] = None
    threshold: int


class LoginResultDetail(CamelModel):
    """登录结果详情"""
    locked: bool
    remaining_attempts: Optional[int] = None
    remaining_seconds: Optional[int] = None
    message: str


class OperationLogResponse(CamelModel):
    """操作日志响应"""
    id: int
    user_id: int
    action: str
    resource_type: Optional[str] = None
    resource_id: Optional[int] = None
    detail: Optional[dict] = None
    ip_address: Optional[str] = None
    created_at: Optional[datetime] = None


class LoginLogResponse(CamelModel):
    """登录日志响应"""
    id: int
    user_id: int
    ip_address: Optional[str] = None
    status: str
    failure_reason: Optional[str] = None
    created_at: Optional[datetime] = None


class PasswordExpiryStatus(CamelModel):
    """密码过期状态"""
    expired: bool
    expiring_soon: bool
    days_remaining: int
    message: Optional[str] = None


class PasswordSuggestions(CamelModel):
    """密码建议"""
    suggestions: List[str]