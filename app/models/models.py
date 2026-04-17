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
    annualLeaveBalance = Column(Float, default=0)
    sickLeaveBalance = Column(Float, default=0)
    isActive = Column(Boolean, default=True)
    createdAt = Column(DateTime, server_default=func.now())


class MeetingRoom(Base):
    """会议室表"""
    __tablename__ = "meeting_rooms"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(100), nullable=False)
    capacity = Column(Integer, default=10)
    location = Column(String(200))
    equipment = Column(Text)  # JSON 格式存储设备列表
    description = Column(Text)
    isActive = Column(Boolean, default=True)
    createdAt = Column(DateTime, server_default=func.now())


class Reservation(Base):
    """预定记录表"""
    __tablename__ = "reservations"

    id = Column(Integer, primary_key=True, index=True)
    roomId = Column(Integer, index=True, nullable=False)
    userId = Column(Integer, index=True, nullable=False)
    title = Column(String(200), nullable=False)
    start = Column("start", String(20), nullable=False)  # YYYY-MM-DD HH:mm
    end = Column("end", String(20), nullable=False)
    status = Column(String(20), default="confirmed")  # confirmed/cancelled
    createdAt = Column(DateTime, server_default=func.now())


class Trip(Base):
    """差旅申请表"""
    __tablename__ = "trips"

    id = Column(Integer, primary_key=True, index=True)
    userId = Column(Integer, index=True, nullable=False)
    destination = Column(String(200), nullable=False)
    reason = Column(Text)
    startDate = Column(String(10), nullable=False)  # YYYY-MM-DD
    endDate = Column(String(10), nullable=False)
    estTransportFee = Column(Float, default=0)
    estAccomFee = Column(Float, default=0)
    status = Column(String(20), default="pending")  # pending/approved/rejected
    approvalComment = Column(Text)
    approvedBy = Column(Integer)
    approvedAt = Column(DateTime)
    createdAt = Column(DateTime, server_default=func.now())


class Leave(Base):
    """请假申请表"""
    __tablename__ = "leaves"

    id = Column(Integer, primary_key=True, index=True)
    userId = Column(Integer, index=True, nullable=False)
    leaveType = Column(String(20), nullable=False)  # annual/sick/personal
    startDate = Column(String(10), nullable=False)
    endDate = Column(String(10), nullable=False)
    reason = Column(Text)
    status = Column(String(20), default="pending")
    approvalComment = Column(Text)
    approvedBy = Column(Integer)
    approvedAt = Column(DateTime)
    createdAt = Column(DateTime, server_default=func.now())


class Attendance(Base):
    """考勤打卡表"""
    __tablename__ = "attendances"

    id = Column(Integer, primary_key=True, index=True)
    userId = Column(Integer, index=True, nullable=False)
    date = Column(String(10), index=True, nullable=False)  # YYYY-MM-DD
    checkInTime = Column(String(10))  # HH:mm
    checkOutTime = Column(String(10))
    isLate = Column(Boolean, default=False)
    isEarlyLeave = Column(Boolean, default=False)
    status = Column(String(20), default="normal")
    createdAt = Column(DateTime, server_default=func.now())


class MakeUpRequest(Base):
    """补卡申请表"""
    __tablename__ = "make_up_requests"

    id = Column(Integer, primary_key=True, index=True)
    userId = Column(Integer, index=True, nullable=False)
    date = Column(String(10), nullable=False)
    type = Column(String(20), nullable=False)  # checkIn/checkOut
    reason = Column(Text)
    status = Column(String(20), default="pending")
    approvedBy = Column(Integer)
    approvedAt = Column(DateTime)
    createdAt = Column(DateTime, server_default=func.now())


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
    createdAt = Column(DateTime, server_default=func.now())


class Document(Base):
    """文档表"""
    __tablename__ = "documents"

    id = Column(Integer, primary_key=True, index=True)
    categoryId = Column(Integer, index=True)
    name = Column(String(200), nullable=False)
    description = Column(Text)
    fileSize = Column(Integer)
    fileType = Column(String(50))
    uploadBy = Column(Integer, index=True)
    tags = Column(Text)  # JSON 格式
    createdAt = Column(DateTime, server_default=func.now())


class Todo(Base):
    """待办事项表"""
    __tablename__ = "todos"

    id = Column(Integer, primary_key=True, index=True)
    userId = Column(Integer, index=True, nullable=False)
    title = Column(String(200), nullable=False)
    description = Column(Text)
    taskDate = Column(String(10))  # YYYY-MM-DD
    dueDate = Column(String(10))
    status = Column(String(20), default="pending")  # pending/completed
    priority = Column(Integer, default=2)  # 1-高 2-中 3-低
    relatedType = Column(String(50))
    relatedId = Column(Integer)
    completedAt = Column(DateTime)
    createdAt = Column(DateTime, server_default=func.now())


class Announcement(Base):
    """公告通知表"""
    __tablename__ = "announcements"

    id = Column(Integer, primary_key=True, index=True)
    title = Column(String(200), nullable=False)
    content = Column(Text, nullable=False)
    summary = Column(String(500))
    category = Column(String(20), default="notice")  # policy/activity/notice
    categoryLabel = Column(String(50))
    isTop = Column(Boolean, default=False)
    isRemind = Column(Boolean, default=False)
    publishTime = Column(DateTime)
    readBy = Column(Text)  # JSON 数组存储已读用户ID
    popupShown = Column(Text)  # JSON 数组
    createdAt = Column(DateTime, server_default=func.now())


class UserPreference(Base):
    """用户偏好设置表"""
    __tablename__ = "user_preferences"

    id = Column(Integer, primary_key=True, index=True)
    userId = Column(Integer, index=True, nullable=False)
    theme = Column(String(20), default="light")
    language = Column(String(10), default="zh")
    notificationsEnabled = Column(Boolean, default=True)
    createdAt = Column(DateTime, server_default=func.now())


class TripTemplate(Base):
    """出差模板表"""
    __tablename__ = "trip_templates"

    id = Column(Integer, primary_key=True, index=True)
    userId = Column(Integer, index=True, nullable=False)
    name = Column(String(100), nullable=False)
    destination = Column(String(200))
    reason = Column(Text)
    estTransportFee = Column(Float, default=0)
    estAccomFee = Column(Float, default=0)
    useCount = Column(Integer, default=0)
    lastUsedAt = Column(DateTime)
    createdAt = Column(DateTime, server_default=func.now())


class CityConfig(Base):
    """城市配置表"""
    __tablename__ = "city_configs"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(100), nullable=False)
    province = Column(String(100))
    transportFeeBase = Column(Float, default=0)
    accomFeeBase = Column(Float, default=0)
    createdAt = Column(DateTime, server_default=func.now())


class HolidayConfig(Base):
    """节假日配置表"""
    __tablename__ = "holiday_configs"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(100), nullable=False)
    date = Column(String(10), nullable=False)  # YYYY-MM-DD
    type = Column(String(20))  # holiday/workday
    createdAt = Column(DateTime, server_default=func.now())


class DocumentViewLog(Base):
    """文档查看日志表"""
    __tablename__ = "document_view_logs"

    id = Column(Integer, primary_key=True, index=True)
    documentId = Column(Integer, index=True, nullable=False)
    userId = Column(Integer, index=True, nullable=False)
    viewTime = Column(DateTime, server_default=func.now())


class SearchHistory(Base):
    """搜索历史表"""
    __tablename__ = "search_histories"

    id = Column(Integer, primary_key=True, index=True)
    userId = Column(Integer, index=True, nullable=False)
    keyword = Column(String(200), nullable=False)
    searchType = Column(String(50))
    createdAt = Column(DateTime, server_default=func.now())


class ExpenseClaim(Base):
    """报销单表"""
    __tablename__ = "expense_claims"

    id = Column(Integer, primary_key=True, index=True)
    userId = Column(Integer, index=True, nullable=False)
    tripId = Column(Integer, index=True)
    expenses = Column(Text)  # JSON 格式存储费用明细
    totalEstimated = Column(Float, default=0)
    totalActual = Column(Float, default=0)
    status = Column(String(20), default="draft")  # draft/submitted/approved
    submittedAt = Column(DateTime)
    approvedBy = Column(Integer)
    approvedAt = Column(DateTime)
    createdAt = Column(DateTime, server_default=func.now())
    updatedAt = Column(DateTime, server_default=func.now())