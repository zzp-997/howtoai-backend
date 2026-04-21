"""
考勤打卡相关 Schema
"""
from pydantic import BaseModel
from typing import Optional
from datetime import datetime
from app.schemas.common import CamelModel


class AttendanceResponse(CamelModel):
    """考勤记录响应"""
    id: int
    user_id: int
    date: str
    check_in_time: Optional[str] = None
    check_out_time: Optional[str] = None
    is_late: bool = False
    is_early_leave: bool = False
    status: str = "normal"
    created_at: Optional[datetime] = None


class AttendanceStats(BaseModel):
    """考勤统计"""
    total: int
    normal: int
    late: int
    missing_check_in: int
    missing_check_out: int


class MakeUpRequestBase(CamelModel):
    """补卡申请基础"""
    date: str  # YYYY-MM-DD
    type: str  # checkIn/checkOut
    reason: Optional[str] = None


class MakeUpRequestCreate(MakeUpRequestBase):
    """创建补卡申请"""
    pass


class MakeUpRequestResponse(MakeUpRequestBase):
    """补卡申请响应"""
    id: int
    user_id: int
    status: str = "pending"
    approved_by: Optional[int] = None
    approved_at: Optional[datetime] = None
    created_at: Optional[datetime] = None
