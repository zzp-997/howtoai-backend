"""
用户相关 Schema
"""
from pydantic import BaseModel
from typing import Optional
from datetime import datetime
from app.schemas.common import CamelModel


class UserBase(CamelModel):
    """用户基础信息"""
    username: str
    name: str
    role: str = "user"
    department: Optional[str] = None
    position: Optional[str] = None
    phone: Optional[str] = None
    email: Optional[str] = None


class UserCreate(UserBase):
    """创建用户"""
    password: str


class UserUpdate(CamelModel):
    """更新用户"""
    name: Optional[str] = None
    department: Optional[str] = None
    position: Optional[str] = None
    phone: Optional[str] = None
    email: Optional[str] = None
    avatar: Optional[str] = None
    annual_leave_balance: Optional[float] = None
    sick_leave_balance: Optional[float] = None


class UserResponse(UserBase):
    """用户响应"""
    id: int
    avatar: Optional[str] = None
    annual_leave_balance: float = 0
    sick_leave_balance: float = 0
    is_active: bool = True
    created_at: Optional[datetime] = None


class LoginRequest(BaseModel):
    """登录请求"""
    username: str
    password: str
    login_type: int = 1


class LoginData(CamelModel):
    """登录数据"""
    token: str
    user: UserResponse


class LoginResponse(BaseModel):
    """登录响应"""
    code: int = 200
    message: str = "success"
    data: Optional[LoginData] = None


class TokenData(CamelModel):
    """Token 数据"""
    user_id: int
    username: str
    role: str
