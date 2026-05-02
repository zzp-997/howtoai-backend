"""
消息模块数据模型
"""
from datetime import datetime
from sqlalchemy import Column, Integer, String, Boolean, Text, DateTime
from sqlalchemy.sql import func
from app.core.database import Base


class Message(Base):
    """消息表"""
    __tablename__ = "messages"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, nullable=False, index=True)
    type = Column(String(20), nullable=False, index=True)  # approval/system/task
    title = Column(String(200), nullable=False)
    content = Column(Text)
    related_type = Column(String(50), index=True)  # 关联类型
    related_id = Column(Integer, index=True)  # 关联ID
    is_read = Column(Boolean, default=False, index=True)
    read_at = Column(DateTime)
    created_at = Column(DateTime, server_default=func.now())
