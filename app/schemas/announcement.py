"""
公告通知相关 Schema
"""
import json
from pydantic import field_validator
from typing import Optional, List
from datetime import datetime
from app.schemas.common import CamelModel


class AnnouncementBase(CamelModel):
    """公告基础"""
    title: str
    content: str
    summary: Optional[str] = None
    category: str = "notice"  # policy/activity/notice
    is_top: bool = False
    is_remind: bool = False


class AnnouncementCreate(AnnouncementBase):
    """创建公告"""
    pass


class AnnouncementUpdate(CamelModel):
    """更新公告"""
    title: Optional[str] = None
    content: Optional[str] = None
    summary: Optional[str] = None
    category: Optional[str] = None
    is_top: Optional[bool] = None
    is_remind: Optional[bool] = None


class AnnouncementResponse(AnnouncementBase):
    """公告响应"""
    id: int
    category_label: Optional[str] = None
    publish_time: Optional[datetime] = None
    read_by: List[int] = []
    created_at: Optional[datetime] = None

    @field_validator('read_by', mode='before')
    @classmethod
    def parse_read_by(cls, v):
        """解析 read_by 字段，支持 JSON 字符串"""
        if v is None:
            return []
        if isinstance(v, list):
            return v
        if isinstance(v, str):
            try:
                result = json.loads(v)
                return result if isinstance(result, list) else []
            except:
                return []
        return []
