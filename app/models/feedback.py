"""
意见反馈数据模型
"""
from datetime import datetime
from sqlalchemy import Column, Integer, String, Text, DateTime, ForeignKey, JSON
from sqlalchemy.sql import func
from sqlalchemy.orm import relationship
from app.core.database import Base


class Feedback(Base):
    """意见反馈表"""
    __tablename__ = "feedbacks"

    id = Column(Integer, primary_key=True, index=True)
    feedback_no = Column(String(50), unique=True, nullable=False, index=True)
    user_id = Column(Integer, nullable=False, index=True)
    user_name = Column(String(100))
    type = Column(String(20), nullable=False, index=True)  # suggestion/bug/optimization/other
    title = Column(String(200), nullable=False)
    content = Column(Text, nullable=False)
    images = Column(JSON)  # 图片列表
    status = Column(String(20), default="pending", index=True)  # pending/processing/replied/closed
    handler_id = Column(Integer, index=True)  # 处理人ID
    handler_name = Column(String(100))  # 处理人姓名
    reply_content = Column(Text)  # 回复内容
    replied_at = Column(DateTime)  # 回复时间
    closed_at = Column(DateTime)  # 关闭时间
    created_at = Column(DateTime, server_default=func.now())
    updated_at = Column(DateTime, server_default=func.now(), onupdate=func.now())
