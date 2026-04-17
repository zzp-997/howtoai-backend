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
]