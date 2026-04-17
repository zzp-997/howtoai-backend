"""
待办事项相关 Schema
"""
from pydantic import BaseModel
from typing import Optional
from datetime import datetime


class TodoBase(BaseModel):
    """待办基础"""
    title: str
    description: Optional[str] = None
    taskDate: Optional[str] = None  # YYYY-MM-DD
    dueDate: Optional[str] = None
    priority: int = 2  # 1-高 2-中 3-低
    relatedType: Optional[str] = None
    relatedId: Optional[int] = None


class TodoCreate(TodoBase):
    """创建待办"""
    pass


class TodoUpdate(BaseModel):
    """更新待办"""
    title: Optional[str] = None
    description: Optional[str] = None
    taskDate: Optional[str] = None
    dueDate: Optional[str] = None
    priority: Optional[int] = None
    status: Optional[str] = None


class TodoResponse(TodoBase):
    """待办响应"""
    id: int
    userId: int
    status: str = "pending"
    completedAt: Optional[datetime] = None
    createdAt: Optional[datetime] = None

    class Config:
        from_attributes = True