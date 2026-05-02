"""
消息模块相关 Schema
"""
from pydantic import BaseModel
from typing import Optional
from datetime import datetime
from app.schemas.common import CamelModel


# ============ Message 消息 ============

class MessageBase(CamelModel):
    """消息基础"""
    type: str  # approval/system/task
    title: str
    content: Optional[str] = None
    related_type: Optional[str] = None  # 关联类型
    related_id: Optional[int] = None  # 关联ID


class MessageCreate(MessageBase):
    """创建消息"""
    user_id: int


class MessageUpdate(CamelModel):
    """更新消息"""
    is_read: Optional[bool] = None
    read_at: Optional[datetime] = None


class MessageResponse(MessageBase):
    """消息响应"""
    id: int
    user_id: int
    is_read: bool = False
    read_at: Optional[datetime] = None
    created_at: Optional[datetime] = None


class MessageQuery(CamelModel):
    """消息查询参数"""
    user_id: Optional[int] = None
    type: Optional[str] = None
    is_read: Optional[bool] = None
    related_type: Optional[str] = None
    related_id: Optional[int] = None
    page: int = 1
    page_size: int = 20
