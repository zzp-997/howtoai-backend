"""
意见反馈相关 Schema
"""
from typing import Optional, List
from datetime import datetime
from app.schemas.common import CamelModel


class FeedbackBase(CamelModel):
    """意见反馈基础"""
    type: str  # suggestion/bug/optimization/other
    title: str
    content: str
    images: Optional[List[str]] = None


class FeedbackCreate(FeedbackBase):
    """创建意见反馈"""
    pass


class FeedbackUpdate(CamelModel):
    """更新意见反馈"""
    type: Optional[str] = None
    title: Optional[str] = None
    content: Optional[str] = None
    images: Optional[List[str]] = None
    status: Optional[str] = None


class FeedbackResponse(FeedbackBase):
    """意见反馈响应"""
    id: int
    feedback_no: str
    user_id: int
    user_name: Optional[str] = None
    status: str = "pending"
    handler_id: Optional[int] = None
    handler_name: Optional[str] = None
    reply_content: Optional[str] = None
    replied_at: Optional[datetime] = None
    closed_at: Optional[datetime] = None
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None


class FeedbackReplySchema(CamelModel):
    """意见反馈回复"""
    reply_content: str


class FeedbackQuerySchema(CamelModel):
    """意见反馈查询"""
    type: Optional[str] = None
    status: Optional[str] = None
    user_id: Optional[int] = None
    keyword: Optional[str] = None
    start_date: Optional[datetime] = None
    end_date: Optional[datetime] = None
