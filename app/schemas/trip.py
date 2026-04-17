"""
差旅申请相关 Schema
"""
from pydantic import BaseModel
from typing import Optional
from datetime import datetime


class TripBase(BaseModel):
    """差旅基础"""
    destination: str
    reason: Optional[str] = None
    startDate: str  # YYYY-MM-DD
    endDate: str
    estTransportFee: float = 0
    estAccomFee: float = 0


class TripCreate(TripBase):
    """创建差旅申请"""
    pass


class TripUpdate(BaseModel):
    """更新差旅申请"""
    destination: Optional[str] = None
    reason: Optional[str] = None
    startDate: Optional[str] = None
    endDate: Optional[str] = None
    estTransportFee: Optional[float] = None
    estAccomFee: Optional[float] = None


class TripApprove(BaseModel):
    """审批差旅申请"""
    approved: bool
    comment: Optional[str] = None


class TripResponse(TripBase):
    """差旅申请响应"""
    id: int
    userId: int
    status: str = "pending"
    approvalComment: Optional[str] = None
    approvedBy: Optional[int] = None
    approvedAt: Optional[datetime] = None
    createdAt: Optional[datetime] = None

    class Config:
        from_attributes = True