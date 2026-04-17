"""
请假申请相关 Schema
"""
from pydantic import BaseModel
from typing import Optional
from datetime import datetime


class LeaveBase(BaseModel):
    """请假基础"""
    leaveType: str  # annual/sick/personal
    startDate: str  # YYYY-MM-DD
    endDate: str
    reason: Optional[str] = None


class LeaveCreate(LeaveBase):
    """创建请假申请"""
    pass


class LeaveUpdate(BaseModel):
    """更新请假申请"""
    leaveType: Optional[str] = None
    startDate: Optional[str] = None
    endDate: Optional[str] = None
    reason: Optional[str] = None


class LeaveApprove(BaseModel):
    """审批请假申请"""
    approved: bool
    comment: Optional[str] = None


class LeaveResponse(LeaveBase):
    """请假申请响应"""
    id: int
    userId: int
    status: str = "pending"
    approvalComment: Optional[str] = None
    approvedBy: Optional[int] = None
    approvedAt: Optional[datetime] = None
    createdAt: Optional[datetime] = None

    class Config:
        from_attributes = True