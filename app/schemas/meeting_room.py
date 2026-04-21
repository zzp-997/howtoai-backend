"""
会议室相关 Schema
"""
import json
from pydantic import field_validator
from typing import Optional, List
from datetime import datetime
from app.schemas.common import CamelModel


class MeetingRoomBase(CamelModel):
    """会议室基础"""
    name: str
    capacity: int = 10
    location: Optional[str] = None
    equipment: Optional[List[str]] = None
    description: Optional[str] = None


class MeetingRoomCreate(MeetingRoomBase):
    """创建会议室"""
    pass


class MeetingRoomUpdate(CamelModel):
    """更新会议室"""
    name: Optional[str] = None
    capacity: Optional[int] = None
    location: Optional[str] = None
    equipment: Optional[List[str]] = None
    description: Optional[str] = None
    is_active: Optional[bool] = None


class MeetingRoomResponse(MeetingRoomBase):
    """会议室响应"""
    id: int
    is_active: bool = True
    created_at: Optional[datetime] = None

    @field_validator('equipment', mode='before')
    @classmethod
    def parse_equipment(cls, v):
        """解析 equipment 字段，支持 JSON 字符串"""
        if v is None:
            return []
        if isinstance(v, list):
            return v
        if isinstance(v, str):
            try:
                return json.loads(v)
            except:
                return []
        return []
