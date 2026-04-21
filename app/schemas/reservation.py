"""
预定相关 Schema
"""
from pydantic import BaseModel
from typing import Optional
from datetime import datetime
from app.schemas.common import CamelModel


class ReservationBase(CamelModel):
    """预定基础"""
    room_id: int
    title: str
    start_time: str  # YYYY-MM-DD HH:mm
    end_time: str


class ReservationCreate(ReservationBase):
    """创建预定"""
    pass


class ReservationUpdate(CamelModel):
    """更新预定"""
    title: Optional[str] = None
    start_time: Optional[str] = None
    end_time: Optional[str] = None
    status: Optional[str] = None


class ReservationResponse(ReservationBase):
    """预定响应"""
    id: int
    user_id: int
    status: str = "confirmed"
    created_at: Optional[datetime] = None


class ConflictCheck(BaseModel):
    """冲突检查请求"""
    room_id: int
    start_time: str
    end_time: str
    exclude_id: Optional[int] = None
