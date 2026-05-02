"""
任务协作相关数据模型
"""
from sqlalchemy import Column, Integer, String, DateTime, Text, Boolean, JSON
from sqlalchemy.sql import func
from app.core.database import Base


class Task(Base):
    """任务表"""
    __tablename__ = "tasks"

    id = Column(Integer, primary_key=True, index=True)
    title = Column(String(200), nullable=False)
    description = Column(Text)
    priority = Column(String(20), default="medium")  # low/medium/high
    status = Column(String(20), default="todo")  # todo/in_progress/done/closed
    assignee_ids = Column(Text)  # JSON数组存储负责人ID列表
    watcher_ids = Column(Text)  # JSON数组存储关注者ID列表
    due_date = Column(String(19))  # YYYY-MM-DD HH:MM:SS
    parent_id = Column(Integer, index=True)  # 父任务ID（用于子任务）
    project_id = Column(Integer, index=True)  # 项目ID
    tags = Column(Text)  # JSON数组存储标签
    completed_at = Column(DateTime)
    created_by = Column(Integer, index=True)
    created_at = Column(DateTime, server_default=func.now())
    updated_at = Column(DateTime, server_default=func.now(), onupdate=func.now())


class TaskSubtask(Base):
    """任务子任务表"""
    __tablename__ = "task_subtasks"

    id = Column(Integer, primary_key=True, index=True)
    task_id = Column(Integer, index=True, nullable=False)
    title = Column(String(200), nullable=False)
    completed = Column(Boolean, default=False)
    assignee_id = Column(Integer, index=True)
    due_date = Column(String(10))
    completed_at = Column(DateTime)
    created_at = Column(DateTime, server_default=func.now())
    updated_at = Column(DateTime, server_default=func.now(), onupdate=func.now())


class TaskComment(Base):
    """任务评论表"""
    __tablename__ = "task_comments"

    id = Column(Integer, primary_key=True, index=True)
    task_id = Column(Integer, index=True, nullable=False)
    user_id = Column(Integer, index=True, nullable=False)
    content = Column(Text, nullable=False)
    mention_users = Column(Text)  # JSON数组存储@提及的用户ID
    parent_id = Column(Integer, index=True)  # 回复的评论ID
    created_at = Column(DateTime, server_default=func.now())
    updated_at = Column(DateTime, server_default=func.now(), onupdate=func.now())


class TaskActivity(Base):
    """任务动态表"""
    __tablename__ = "task_activities"

    id = Column(Integer, primary_key=True, index=True)
    task_id = Column(Integer, index=True, nullable=False)
    user_id = Column(Integer, index=True, nullable=False)
    action_type = Column(String(30), nullable=False)  # create/update/status_change/assign/comment/subtask/watcher/delete
    action_detail = Column(Text)  # JSON格式存储变更详情
    created_at = Column(DateTime, server_default=func.now())
