"""
预定相关 Schema
"""
from pydantic import BaseModel
from typing import Optional
from datetime import datetime


class ReservationBase(BaseModel):
    """预定基础"""
    roomId: int
    title: str
    start: str  # YYYY-MM-DD HH:mm
    end: str


class ReservationCreate(ReservationBase):
    """创建预定"""
    pass


class ReservationUpdate(BaseModel):
    """更新预定"""
    title: Optional[str] = None
    start: Optional[str] = None
    end: Optional[str] = None
    status: Optional[str] = None


class ReservationResponse(ReservationBase):
    """预定响应"""
    id: int
    userId: int
    status: str = "confirmed"
    createdAt: Optional[datetime] = None

    class Config:
        from_attributes = True


class ConflictCheck(BaseModel):
    """冲突检查请求"""
    roomId: int
    start: str
    end: str
    excludeId: Optional[int] = None