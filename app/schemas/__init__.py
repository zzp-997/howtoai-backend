"""
Schema 导出
"""
from app.schemas.common import ResponseModel, PaginationModel, CamelModel
from app.schemas.user import (
    UserBase, UserCreate, UserUpdate, UserResponse,
    LoginRequest, LoginResponse, LoginData, TokenData
)
from app.schemas.meeting_room import (
    MeetingRoomBase, MeetingRoomCreate, MeetingRoomUpdate, MeetingRoomResponse
)
from app.schemas.reservation import (
    ReservationBase, ReservationCreate, ReservationUpdate, ReservationResponse, ConflictCheck
)
from app.schemas.trip import (
    TripBase, TripCreate, TripUpdate, TripApprove, TripResponse
)
from app.schemas.leave import (
    LeaveBase, LeaveCreate, LeaveUpdate, LeaveApprove, LeaveResponse
)
from app.schemas.attendance import (
    AttendanceResponse, AttendanceStats, MakeUpRequestBase, MakeUpRequestCreate, MakeUpRequestResponse
)
from app.schemas.todo import (
    TodoBase, TodoCreate, TodoUpdate, TodoResponse
)
from app.schemas.announcement import (
    AnnouncementBase, AnnouncementCreate, AnnouncementUpdate, AnnouncementResponse
)
from app.schemas.document import (
    DocumentCategoryBase, DocumentCategoryCreate, DocumentCategoryResponse,
    DocumentBase, DocumentCreate, DocumentResponse
)
from app.schemas.expense import (
    ExpenseItem, ExpenseClaimBase, ExpenseClaimCreate, ExpenseClaimUpdate, ExpenseClaimResponse
)
from app.schemas.config import (
    AttendanceConfigBase, AttendanceConfigCreate, AttendanceConfigUpdate, AttendanceConfigResponse,
    UserPreferenceBase, UserPreferenceCreate, UserPreferenceUpdate, UserPreferenceResponse,
    TripTemplateBase, TripTemplateCreate, TripTemplateUpdate, TripTemplateResponse,
    CityConfigBase, CityConfigCreate, CityConfigUpdate, CityConfigResponse,
    HolidayConfigBase, HolidayConfigCreate, HolidayConfigUpdate, HolidayConfigResponse
)
from app.schemas.approval import (
    ApprovalChainCreate, ApprovalChainUpdate, ApprovalChainResponse,
    ApprovalNodeCreate, ApprovalNodeResponse,
    ApprovalRequestCreate, ApprovalRequestResponse,
    ApprovalRecordResponse, ApprovalReminderResponse,
    ApprovalChainQuery, ApprovalRequestQuery
)
from app.schemas.message import (
    MessageBase, MessageCreate, MessageResponse, MessageQuery
)
from app.schemas.feedback import (
    FeedbackBase, FeedbackCreate, FeedbackResponse, FeedbackReplySchema, FeedbackQuerySchema
)
from app.schemas.stats import (
    MeetingStatsResponse, AttendanceStatsResponse, ApprovalStatsResponse,
    DashboardStatsResponse, ExportRequest, ExportResponse, UserStatsResponse
)
from app.schemas.knowledge import (
    KnowledgeCategoryCreate, KnowledgeCategoryUpdate, KnowledgeCategoryResponse,
    KnowledgeArticleCreate, KnowledgeArticleUpdate, KnowledgeArticleResponse,
    KnowledgeArticleListResponse, KnowledgeSearchQuery, KnowledgeSearchResult,
    KnowledgeArticleLikeResponse, KnowledgeArticleViewResponse
)
from app.schemas.task import (
    TaskBase, TaskCreate, TaskUpdate, TaskStatusUpdate, TaskAssigneesUpdate,
    TaskWatchersUpdate, TaskWatchUpdate, TaskResponse, TaskListResponse, TaskQuery,
    SubtaskCreate, SubtaskUpdate, SubtaskResponse,
    CommentCreate, CommentUpdate, CommentResponse, CommentListResponse,
    ActivityResponse, ActivityListResponse,
    BatchStatusUpdate, BatchDelete, BatchResult,
    TaskStatsResponse, KanbanStatsResponse, UserTaskStatsResponse
)

__all__ = [
    # 通用
    "ResponseModel", "PaginationModel",
    # 用户
    "UserBase", "UserCreate", "UserUpdate", "UserResponse",
    "LoginRequest", "LoginResponse", "LoginData", "TokenData",
    # 会议室
    "MeetingRoomBase", "MeetingRoomCreate", "MeetingRoomUpdate", "MeetingRoomResponse",
    # 预定
    "ReservationBase", "ReservationCreate", "ReservationUpdate", "ReservationResponse", "ConflictCheck",
    # 差旅
    "TripBase", "TripCreate", "TripUpdate", "TripApprove", "TripResponse",
    # 请假
    "LeaveBase", "LeaveCreate", "LeaveUpdate", "LeaveApprove", "LeaveResponse",
    # 考勤
    "AttendanceResponse", "AttendanceStats", "MakeUpRequestBase", "MakeUpRequestCreate", "MakeUpRequestResponse",
    # 待办
    "TodoBase", "TodoCreate", "TodoUpdate", "TodoResponse",
    # 公告
    "AnnouncementBase", "AnnouncementCreate", "AnnouncementUpdate", "AnnouncementResponse",
    # 文档
    "DocumentCategoryBase", "DocumentCategoryCreate", "DocumentCategoryResponse",
    "DocumentBase", "DocumentCreate", "DocumentResponse",
    # 报销
    "ExpenseItem", "ExpenseClaimBase", "ExpenseClaimCreate", "ExpenseClaimUpdate", "ExpenseClaimResponse",
    # 配置
    "AttendanceConfigBase", "AttendanceConfigCreate", "AttendanceConfigUpdate", "AttendanceConfigResponse",
    "UserPreferenceBase", "UserPreferenceCreate", "UserPreferenceUpdate", "UserPreferenceResponse",
    "TripTemplateBase", "TripTemplateCreate", "TripTemplateUpdate", "TripTemplateResponse",
    "CityConfigBase", "CityConfigCreate", "CityConfigUpdate", "CityConfigResponse",
    "HolidayConfigBase", "HolidayConfigCreate", "HolidayConfigUpdate", "HolidayConfigResponse",
    # 审批
    "ApprovalChainCreate", "ApprovalChainUpdate", "ApprovalChainResponse",
    "ApprovalNodeCreate", "ApprovalNodeResponse",
    "ApprovalRequestCreate", "ApprovalRequestResponse",
    "ApprovalRecordResponse", "ApprovalReminderResponse",
    "ApprovalChainQuery", "ApprovalRequestQuery",
    # 消息
    "MessageBase", "MessageCreate", "MessageResponse", "MessageQuery",
    # 反馈
    "FeedbackBase", "FeedbackCreate", "FeedbackResponse", "FeedbackReplySchema", "FeedbackQuerySchema",
    # 统计
    "MeetingStatsResponse", "AttendanceStatsResponse", "ApprovalStatsResponse",
    "DashboardStatsResponse", "ExportRequest", "ExportResponse", "UserStatsResponse",
    # 知识库
    "KnowledgeCategoryCreate", "KnowledgeCategoryUpdate", "KnowledgeCategoryResponse",
    "KnowledgeArticleCreate", "KnowledgeArticleUpdate", "KnowledgeArticleResponse",
    "KnowledgeArticleListResponse", "KnowledgeSearchQuery", "KnowledgeSearchResult",
    "KnowledgeArticleLikeResponse", "KnowledgeArticleViewResponse",
    # 任务
    "TaskBase", "TaskCreate", "TaskUpdate", "TaskStatusUpdate", "TaskAssigneesUpdate",
    "TaskWatchersUpdate", "TaskWatchUpdate", "TaskResponse", "TaskListResponse", "TaskQuery",
    "SubtaskCreate", "SubtaskUpdate", "SubtaskResponse",
    "CommentCreate", "CommentUpdate", "CommentResponse", "CommentListResponse",
    "ActivityResponse", "ActivityListResponse",
    "BatchStatusUpdate", "BatchDelete", "BatchResult",
    "TaskStatsResponse", "KanbanStatsResponse", "UserTaskStatsResponse",
]