"""
公告通知相关 Schema
"""
import json
from pydantic import BaseModel, field_validator
from typing import Optional, List
from datetime import datetime


class AnnouncementBase(BaseModel):
    """公告基础"""
    title: str
    content: str
    summary: Optional[str] = None
    category: str = "notice"  # policy/activity/notice
    isTop: bool = False
    isRemind: bool = False


class AnnouncementCreate(AnnouncementBase):
    """创建公告"""
    pass


class AnnouncementUpdate(BaseModel):
    """更新公告"""
    title: Optional[str] = None
    content: Optional[str] = None
    summary: Optional[str] = None
    category: Optional[str] = None
    isTop: Optional[bool] = None
    isRemind: Optional[bool] = None


class AnnouncementResponse(AnnouncementBase):
    """公告响应"""
    id: int
    categoryLabel: Optional[str] = None
    publishTime: Optional[datetime] = None
    readBy: List[int] = []
    createdAt: Optional[datetime] = None

    @field_validator('readBy', mode='before')
    @classmethod
    def parse_read_by(cls, v):
        """解析 readBy 字段，支持 JSON 字符串"""
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

    model_config = {'from_attributes': True}