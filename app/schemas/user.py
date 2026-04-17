"""
用户相关 Schema
"""
from pydantic import BaseModel
from typing import Optional
from datetime import datetime


class UserBase(BaseModel):
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


class UserUpdate(BaseModel):
    """更新用户"""
    name: Optional[str] = None
    department: Optional[str] = None
    position: Optional[str] = None
    phone: Optional[str] = None
    email: Optional[str] = None
    avatar: Optional[str] = None
    annualLeaveBalance: Optional[float] = None
    sickLeaveBalance: Optional[float] = None


class UserResponse(UserBase):
    """用户响应"""
    id: int
    avatar: Optional[str] = None
    annualLeaveBalance: float = 0
    sickLeaveBalance: float = 0
    isActive: bool = True
    createdAt: Optional[datetime] = None

    class Config:
        from_attributes = True


class LoginRequest(BaseModel):
    """登录请求"""
    username: str
    password: str
    loginType: int = 1  # 1: 密码登录


class LoginData(BaseModel):
    """登录数据"""
    token: str
    user: UserResponse


class LoginResponse(BaseModel):
    """登录响应"""
    code: int = 200
    message: str = "success"
    data: Optional[LoginData] = None


class TokenData(BaseModel):
    """Token 数据"""
    userId: int
    username: str
    role: str
