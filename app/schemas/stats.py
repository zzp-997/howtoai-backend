"""
统计相关 Schema
"""
from pydantic import BaseModel
from typing import Optional, List, Dict, Any
from datetime import datetime
from app.schemas.common import CamelModel


class MeetingStatsResponse(CamelModel):
    """会议使用率统计响应"""
    total_meetings: int
    total_hours: float
    room_usage: List[Dict[str, Any]]
    daily_trend: List[Dict[str, Any]]
    peak_hours: Dict[str, int]


class AttendanceStatsResponse(CamelModel):
    """考勤分析统计响应"""
    total_users: int
    attendance_rate: float
    late_count: int
    early_leave_count: int
    absent_count: int
    department_stats: List[Dict[str, Any]]
    daily_trend: List[Dict[str, Any]]


class ApprovalStatsResponse(CamelModel):
    """审批统计响应"""
    total_requests: int
    pending_count: int
    approved_count: int
    rejected_count: int
    avg_processing_hours: float
    type_stats: List[Dict[str, Any]]
    daily_trend: List[Dict[str, Any]]


class DashboardStatsResponse(CamelModel):
    """综合大屏数据响应"""
    total_users: int
    active_users_today: int
    total_meetings_today: int
    total_pending_approvals: int
    attendance_rate_today: float
    recent_activities: List[Dict[str, Any]]


class ExportRequest(CamelModel):
    """导出请求"""
    export_type: str  # meetings, attendance, approvals, dashboard
    date_from: Optional[str] = None
    date_to: Optional[str] = None
    format: str = "xlsx"


class ExportResponse(CamelModel):
    """导出响应"""
    id: int
    export_type: str
    status: str
    created_at: datetime


class UserStatsResponse(CamelModel):
    """用户个人统计响应"""
    total_meetings: int
    total_hours: float
    attendance_rate: float
    pending_approvals: int
    completed_tasks: int
    pending_tasks: int
    my_activities: List[Dict[str, Any]]
