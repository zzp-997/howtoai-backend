"""
待办事项相关 Schema
"""
from pydantic import BaseModel
from typing import Optional
from datetime import datetime
from app.schemas.common import CamelModel


class TodoBase(CamelModel):
    """待办基础"""
    title: str
    description: Optional[str] = None
    task_date: Optional[str] = None  # YYYY-MM-DD
    due_date: Optional[str] = None
    priority: int = 2  # 1-高 2-中 3-低
    related_type: Optional[str] = None
    related_id: Optional[int] = None


class TodoCreate(TodoBase):
    """创建待办"""
    pass


class TodoUpdate(CamelModel):
    """更新待办"""
    title: Optional[str] = None
    description: Optional[str] = None
    task_date: Optional[str] = None
    due_date: Optional[str] = None
    priority: Optional[int] = None
    status: Optional[str] = None


class TodoResponse(TodoBase):
    """待办响应"""
    id: int
    user_id: int
    status: str = "pending"
    completed_at: Optional[datetime] = None
    created_at: Optional[datetime] = None
