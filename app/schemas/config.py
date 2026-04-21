"""
配置相关 Schema
"""
from pydantic import BaseModel
from typing import Optional
from datetime import datetime
from app.schemas.common import CamelModel


# ==================== 考勤配置 ====================

class AttendanceConfigBase(CamelModel):
    key: str
    value: str


class AttendanceConfigCreate(AttendanceConfigBase):
    pass


class AttendanceConfigUpdate(BaseModel):
    value: str


class AttendanceConfigResponse(AttendanceConfigBase):
    pass


# ==================== 用户偏好 ====================

class UserPreferenceBase(CamelModel):
    theme: str = "light"
    language: str = "zh"
    notifications_enabled: bool = True


class UserPreferenceCreate(UserPreferenceBase):
    user_id: int


class UserPreferenceUpdate(CamelModel):
    theme: Optional[str] = None
    language: Optional[str] = None
    notifications_enabled: Optional[bool] = None


class UserPreferenceResponse(UserPreferenceBase):
    id: int
    user_id: int
    created_at: Optional[datetime] = None


# ==================== 出差模板 ====================

class TripTemplateBase(CamelModel):
    name: str
    destination: Optional[str] = None
    reason: Optional[str] = None
    est_transport_fee: float = 0
    est_accom_fee: float = 0


class TripTemplateCreate(TripTemplateBase):
    user_id: int


class TripTemplateUpdate(CamelModel):
    name: Optional[str] = None
    destination: Optional[str] = None
    reason: Optional[str] = None
    est_transport_fee: Optional[float] = None
    est_accom_fee: Optional[float] = None


class TripTemplateResponse(TripTemplateBase):
    id: int
    user_id: int
    use_count: int = 0
    last_used_at: Optional[datetime] = None
    created_at: Optional[datetime] = None


# ==================== 城市配置 ====================

class CityConfigBase(CamelModel):
    name: str
    province: Optional[str] = None
    transport_fee_base: float = 0
    accom_fee_base: float = 0


class CityConfigCreate(CityConfigBase):
    pass


class CityConfigUpdate(CamelModel):
    name: Optional[str] = None
    province: Optional[str] = None
    transport_fee_base: Optional[float] = None
    accom_fee_base: Optional[float] = None


class CityConfigResponse(CityConfigBase):
    id: int
    created_at: Optional[datetime] = None


# ==================== 节假日配置 ====================

class HolidayConfigBase(CamelModel):
    name: str
    date: str  # YYYY-MM-DD
    type: str = "holiday"  # holiday/workday


class HolidayConfigCreate(HolidayConfigBase):
    pass


class HolidayConfigUpdate(CamelModel):
    name: Optional[str] = None
    date: Optional[str] = None
    type: Optional[str] = None


class HolidayConfigResponse(HolidayConfigBase):
    id: int
    created_at: Optional[datetime] = None
