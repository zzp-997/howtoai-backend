"""
差旅申请相关 Schema
"""
from pydantic import BaseModel
from typing import Optional
from datetime import datetime
from app.schemas.common import CamelModel


class TripBase(CamelModel):
    """差旅基础"""
    destination: str
    reason: Optional[str] = None
    start_date: str  # YYYY-MM-DD
    end_date: str
    est_transport_fee: float = 0
    est_accom_fee: float = 0


class TripCreate(TripBase):
    """创建差旅申请"""
    pass


class TripUpdate(CamelModel):
    """更新差旅申请"""
    destination: Optional[str] = None
    reason: Optional[str] = None
    start_date: Optional[str] = None
    end_date: Optional[str] = None
    est_transport_fee: Optional[float] = None
    est_accom_fee: Optional[float] = None


class TripApprove(BaseModel):
    """审批差旅申请"""
    approved: bool
    comment: Optional[str] = None


class TripResponse(TripBase):
    """差旅申请响应"""
    id: int
    user_id: int
    status: str = "pending"
    approval_comment: Optional[str] = None
    approved_by: Optional[int] = None
    approved_at: Optional[datetime] = None
    created_at: Optional[datetime] = None
