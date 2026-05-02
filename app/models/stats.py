"""
数据统计模型
"""
from sqlalchemy import Column, Integer, String, DateTime, Text, JSON
from sqlalchemy.sql import func
from app.core.database import Base


class StatsExport(Base):
    """数据导出记录表"""
    __tablename__ = "stats_exports"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, index=True, nullable=False)
    export_type = Column(String(50), nullable=False)  # meetings, attendance, approvals, dashboard
    date_from = Column(String(10))
    date_to = Column(String(10))
    format = Column(String(10), default="xlsx")
    file_path = Column(String(500))
    status = Column(String(20), default="pending")
    created_at = Column(DateTime, server_default=func.now())
