"""
配置相关 Schema
"""
from pydantic import BaseModel
from typing import Optional
from datetime import datetime


# ==================== 考勤配置 ====================

class AttendanceConfigBase(BaseModel):
    key: str
    value: str


class AttendanceConfigCreate(AttendanceConfigBase):
    pass


class AttendanceConfigUpdate(BaseModel):
    value: str


class AttendanceConfigResponse(AttendanceConfigBase):
    class Config:
        from_attributes = True


# ==================== 用户偏好 ====================

class UserPreferenceBase(BaseModel):
    theme: str = "light"
    language: str = "zh"
    notificationsEnabled: bool = True


class UserPreferenceCreate(UserPreferenceBase):
    userId: int


class UserPreferenceUpdate(BaseModel):
    theme: Optional[str] = None
    language: Optional[str] = None
    notificationsEnabled: Optional[bool] = None


class UserPreferenceResponse(UserPreferenceBase):
    id: int
    userId: int
    createdAt: Optional[datetime] = None

    class Config:
        from_attributes = True


# ==================== 出差模板 ====================

class TripTemplateBase(BaseModel):
    name: str
    destination: Optional[str] = None
    reason: Optional[str] = None
    estTransportFee: float = 0
    estAccomFee: float = 0


class TripTemplateCreate(TripTemplateBase):
    userId: int


class TripTemplateUpdate(BaseModel):
    name: Optional[str] = None
    destination: Optional[str] = None
    reason: Optional[str] = None
    estTransportFee: Optional[float] = None
    estAccomFee: Optional[float] = None


class TripTemplateResponse(TripTemplateBase):
    id: int
    userId: int
    useCount: int = 0
    lastUsedAt: Optional[datetime] = None
    createdAt: Optional[datetime] = None

    class Config:
        from_attributes = True


# ==================== 城市配置 ====================

class CityConfigBase(BaseModel):
    name: str
    province: Optional[str] = None
    transportFeeBase: float = 0
    accomFeeBase: float = 0


class CityConfigCreate(CityConfigBase):
    pass


class CityConfigUpdate(BaseModel):
    name: Optional[str] = None
    province: Optional[str] = None
    transportFeeBase: Optional[float] = None
    accomFeeBase: Optional[float] = None


class CityConfigResponse(CityConfigBase):
    id: int
    createdAt: Optional[datetime] = None

    class Config:
        from_attributes = True


# ==================== 节假日配置 ====================

class HolidayConfigBase(BaseModel):
    name: str
    date: str  # YYYY-MM-DD
    type: str = "holiday"  # holiday/workday


class HolidayConfigCreate(HolidayConfigBase):
    pass


class HolidayConfigUpdate(BaseModel):
    name: Optional[str] = None
    date: Optional[str] = None
    type: Optional[str] = None


class HolidayConfigResponse(HolidayConfigBase):
    id: int
    createdAt: Optional[datetime] = None

    class Config:
        from_attributes = True
