"""
服务导出
"""
from app.services.base import BaseService
from app.services.auth_service import AuthService, auth_service
from app.services.meeting_room_service import MeetingRoomService, meeting_room_service
from app.services.reservation_service import ReservationService, reservation_service
from app.services.trip_service import TripService, trip_service
from app.services.leave_service import LeaveService, leave_service
from app.services.attendance_service import (
    AttendanceService, attendance_service,
    MakeUpRequestService, makeup_request_service
)
from app.services.todo_service import TodoService, todo_service
from app.services.announcement_service import AnnouncementService, announcement_service
from app.services.document_service import DocumentService, document_service, DocumentCategoryService, document_category_service
from app.services.expense_service import ExpenseClaimService, expense_claim_service
from app.services.config_service import (
    AttendanceConfigService, attendance_config_service,
    UserPreferenceService, user_preference_service,
    TripTemplateService, trip_template_service,
    CityConfigService, city_config_service,
    HolidayConfigService, holiday_config_service
)
from app.services.approval_service import ApprovalService, approval_service
from app.services.message_service import MessageService, message_service
from app.services.feedback_service import FeedbackService, feedback_service
from app.services.stats_service import StatsService, stats_service
from app.services.knowledge_service import KnowledgeService, knowledge_service
from app.services.task_service import TaskService, task_service

__all__ = [
    "BaseService",
    "AuthService", "auth_service",
    "MeetingRoomService", "meeting_room_service",
    "ReservationService", "reservation_service",
    "TripService", "trip_service",
    "LeaveService", "leave_service",
    "AttendanceService", "attendance_service",
    "MakeUpRequestService", "makeup_request_service",
    "TodoService", "todo_service",
    "AnnouncementService", "announcement_service",
    "DocumentService", "document_service",
    "DocumentCategoryService", "document_category_service",
    "ExpenseClaimService", "expense_claim_service",
    # 配置服务
    "AttendanceConfigService", "attendance_config_service",
    "UserPreferenceService", "user_preference_service",
    "TripTemplateService", "trip_template_service",
    "CityConfigService", "city_config_service",
    "HolidayConfigService", "holiday_config_service",
    # 审批服务
    "ApprovalService", "approval_service",
    # 消息服务
    "MessageService", "message_service",
    # 反馈服务
    "FeedbackService", "feedback_service",
    # 统计服务
    "StatsService", "stats_service",
    # 知识库服务
    "KnowledgeService", "knowledge_service",
    # 任务服务
    "TaskService", "task_service",
]