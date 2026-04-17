"""
考勤打卡相关 Schema
"""
from pydantic import BaseModel
from typing import Optional
from datetime import datetime


class AttendanceResponse(BaseModel):
    """考勤记录响应"""
    id: int
    userId: int
    date: str
    checkInTime: Optional[str] = None
    checkOutTime: Optional[str] = None
    isLate: bool = False
    isEarlyLeave: bool = False
    status: str = "normal"
    createdAt: Optional[datetime] = None

    class Config:
        from_attributes = True


class AttendanceStats(BaseModel):
    """考勤统计"""
    total: int
    normal: int
    late: int
    missingCheckIn: int
    missingCheckOut: int


class MakeUpRequestBase(BaseModel):
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
    userId: int
    status: str = "pending"
    approvedBy: Optional[int] = None
    approvedAt: Optional[datetime] = None
    createdAt: Optional[datetime] = None

    class Config:
        from_attributes = True