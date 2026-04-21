"""
所有数据模型
"""
from sqlalchemy import Column, Integer, String, Float, DateTime, Boolean, Text, JSON
from sqlalchemy.sql import func
from app.core.database import Base


class User(Base):
    """用户表"""
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    username = Column(String(50), unique=True, index=True, nullable=False)
    password = Column(String(255), nullable=False)
    name = Column(String(50), nullable=False)
    role = Column(String(20), default="user")
    department = Column(String(100))
    position = Column(String(100))
    phone = Column(String(20))
    email = Column(String(100))
    avatar = Column(String(255))
    annual_leave_balance = Column(Float, default=0)
    sick_leave_balance = Column(Float, default=0)
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime, server_default=func.now())


class MeetingRoom(Base):
    """会议室表"""
    __tablename__ = "meeting_rooms"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(100), nullable=False)
    capacity = Column(Integer, default=10)
    location = Column(String(200))
    equipment = Column(Text)
    description = Column(Text)
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime, server_default=func.now())


class Reservation(Base):
    """预定记录表"""
    __tablename__ = "reservations"

    id = Column(Integer, primary_key=True, index=True)
    room_id = Column(Integer, index=True, nullable=False)
    user_id = Column(Integer, index=True, nullable=False)
    title = Column(String(200), nullable=False)
    start_time = Column(String(20), nullable=False)
    end_time = Column(String(20), nullable=False)
    status = Column(String(20), default="confirmed")
    created_at = Column(DateTime, server_default=func.now())


class Trip(Base):
    """差旅申请表"""
    __tablename__ = "trips"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, index=True, nullable=False)
    destination = Column(String(200), nullable=False)
    reason = Column(Text)
    start_date = Column(String(10), nullable=False)
    end_date = Column(String(10), nullable=False)
    est_transport_fee = Column(Float, default=0)
    est_accom_fee = Column(Float, default=0)
    status = Column(String(20), default="pending")
    approval_comment = Column(Text)
    approved_by = Column(Integer)
    approved_at = Column(DateTime)
    created_at = Column(DateTime, server_default=func.now())


class Leave(Base):
    """请假申请表"""
    __tablename__ = "leaves"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, index=True, nullable=False)
    leave_type = Column(String(20), nullable=False)
    start_date = Column(String(10), nullable=False)
    end_date = Column(String(10), nullable=False)
    reason = Column(Text)
    status = Column(String(20), default="pending")
    approval_comment = Column(Text)
    approved_by = Column(Integer)
    approved_at = Column(DateTime)
    created_at = Column(DateTime, server_default=func.now())


class Attendance(Base):
    """考勤打卡表"""
    __tablename__ = "attendances"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, index=True, nullable=False)
    date = Column(String(10), index=True, nullable=False)
    check_in_time = Column(String(10))
    check_out_time = Column(String(10))
    is_late = Column(Boolean, default=False)
    is_early_leave = Column(Boolean, default=False)
    status = Column(String(20), default="normal")
    created_at = Column(DateTime, server_default=func.now())


class MakeUpRequest(Base):
    """补卡申请表"""
    __tablename__ = "make_up_requests"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, index=True, nullable=False)
    date = Column(String(10), nullable=False)
    type = Column(String(20), nullable=False)
    reason = Column(Text)
    status = Column(String(20), default="pending")
    approved_by = Column(Integer)
    approved_at = Column(DateTime)
    created_at = Column(DateTime, server_default=func.now())


class AttendanceConfig(Base):
    """考勤配置表"""
    __tablename__ = "attendance_config"

    key = Column(String(50), primary_key=True)
    value = Column(String(100))


class DocumentCategory(Base):
    """文档分类表"""
    __tablename__ = "document_categories"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(100), nullable=False)
    description = Column(Text)
    created_at = Column(DateTime, server_default=func.now())


class Document(Base):
    """文档表"""
    __tablename__ = "documents"

    id = Column(Integer, primary_key=True, index=True)
    category_id = Column(Integer, index=True)
    name = Column(String(200), nullable=False)
    description = Column(Text)
    file_size = Column(Integer)
    file_type = Column(String(50))
    upload_by = Column(Integer, index=True)
    tags = Column(Text)
    created_at = Column(DateTime, server_default=func.now())


class Todo(Base):
    """待办事项表"""
    __tablename__ = "todos"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, index=True, nullable=False)
    title = Column(String(200), nullable=False)
    description = Column(Text)
    task_date = Column(String(10))
    due_date = Column(String(10))
    status = Column(String(20), default="pending")
    priority = Column(Integer, default=2)
    related_type = Column(String(50))
    related_id = Column(Integer)
    completed_at = Column(DateTime)
    created_at = Column(DateTime, server_default=func.now())


class Announcement(Base):
    """公告通知表"""
    __tablename__ = "announcements"

    id = Column(Integer, primary_key=True, index=True)
    title = Column(String(200), nullable=False)
    content = Column(Text, nullable=False)
    summary = Column(String(500))
    category = Column(String(20), default="notice")
    category_label = Column(String(50))
    is_top = Column(Boolean, default=False)
    is_remind = Column(Boolean, default=False)
    publish_time = Column(DateTime)
    read_by = Column(Text)
    popup_shown = Column(Text)
    created_at = Column(DateTime, server_default=func.now())


class UserPreference(Base):
    """用户偏好设置表"""
    __tablename__ = "user_preferences"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, index=True, nullable=False, unique=True)
    theme = Column(String(20), default="light")
    language = Column(String(10), default="zh")
    notifications_enabled = Column(Boolean, default=True)
    created_at = Column(DateTime, server_default=func.now())


class TripTemplate(Base):
    """出差模板表"""
    __tablename__ = "trip_templates"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, index=True, nullable=False)
    name = Column(String(100), nullable=False)
    destination = Column(String(200))
    reason = Column(Text)
    est_transport_fee = Column(Float, default=0)
    est_accom_fee = Column(Float, default=0)
    use_count = Column(Integer, default=0)
    last_used_at = Column(DateTime)
    created_at = Column(DateTime, server_default=func.now())


class CityConfig(Base):
    """城市配置表"""
    __tablename__ = "city_configs"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(100), nullable=False)
    province = Column(String(100))
    transport_fee_base = Column(Float, default=0)
    accom_fee_base = Column(Float, default=0)
    created_at = Column(DateTime, server_default=func.now())


class HolidayConfig(Base):
    """节假日配置表"""
    __tablename__ = "holiday_configs"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(100), nullable=False)
    date = Column(String(10), nullable=False)
    type = Column(String(20))
    created_at = Column(DateTime, server_default=func.now())


class DocumentViewLog(Base):
    """文档查看日志表"""
    __tablename__ = "document_view_logs"

    id = Column(Integer, primary_key=True, index=True)
    document_id = Column(Integer, index=True, nullable=False)
    user_id = Column(Integer, index=True, nullable=False)
    view_time = Column(DateTime, server_default=func.now())


class SearchHistory(Base):
    """搜索历史表"""
    __tablename__ = "search_histories"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, index=True, nullable=False)
    keyword = Column(String(200), nullable=False)
    search_type = Column(String(50))
    created_at = Column(DateTime, server_default=func.now())


class ExpenseClaim(Base):
    """报销单表"""
    __tablename__ = "expense_claims"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, index=True, nullable=False)
    trip_id = Column(Integer, index=True)
    expenses = Column(Text)
    total_estimated = Column(Float, default=0)
    total_actual = Column(Float, default=0)
    status = Column(String(20), default="draft")
    submitted_at = Column(DateTime)
    approved_by = Column(Integer)
    approved_at = Column(DateTime)
    created_at = Column(DateTime, server_default=func.now())
    updated_at = Column(DateTime, server_default=func.now())
