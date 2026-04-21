"""
请假申请相关 Schema
"""
from pydantic import BaseModel
from typing import Optional
from datetime import datetime
from app.schemas.common import CamelModel


class LeaveBase(CamelModel):
    """请假基础"""
    leave_type: str  # annual/sick/personal
    start_date: str  # YYYY-MM-DD
    end_date: str
    reason: Optional[str] = None


class LeaveCreate(LeaveBase):
    """创建请假申请"""
    pass


class LeaveUpdate(CamelModel):
    """更新请假申请"""
    leave_type: Optional[str] = None
    start_date: Optional[str] = None
    end_date: Optional[str] = None
    reason: Optional[str] = None


class LeaveApprove(BaseModel):
    """审批请假申请"""
    approved: bool
    comment: Optional[str] = None


class LeaveResponse(LeaveBase):
    """请假申请响应"""
    id: int
    user_id: int
    status: str = "pending"
    approval_comment: Optional[str] = None
    approved_by: Optional[int] = None
    approved_at: Optional[datetime] = None
    created_at: Optional[datetime] = None
