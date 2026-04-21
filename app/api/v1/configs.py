"""
配置相关 API
"""
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from typing import List
from app.core.database import get_db
from app.schemas.config import (
    AttendanceConfigCreate, AttendanceConfigUpdate, AttendanceConfigResponse,
    UserPreferenceCreate, UserPreferenceUpdate, UserPreferenceResponse,
    TripTemplateCreate, TripTemplateUpdate, TripTemplateResponse,
    CityConfigCreate, CityConfigUpdate, CityConfigResponse,
    HolidayConfigCreate, HolidayConfigUpdate, HolidayConfigResponse
)
from app.schemas.common import ResponseModel
from app.services.config_service import (
    attendance_config_service, user_preference_service,
    trip_template_service, city_config_service, holiday_config_service
)
from app.api.v1.auth import get_current_user
from app.schemas.user import UserResponse

router = APIRouter(prefix="/configs", tags=["配置管理"])


# ==================== 考勤配置 ====================

@router.get("/attendance", response_model=ResponseModel[List[AttendanceConfigResponse]])
async def get_attendance_configs(
    db: AsyncSession = Depends(get_db),
    current_user: UserResponse = Depends(get_current_user)
):
    """获取考勤配置列表"""
    configs = await attendance_config_service.get_all(db)
    return ResponseModel(data=configs)


@router.post("/attendance", response_model=ResponseModel[AttendanceConfigResponse])
async def set_attendance_config(
    data: AttendanceConfigCreate,
    db: AsyncSession = Depends(get_db),
    current_user: UserResponse = Depends(get_current_user)
):
    """设置考勤配置（管理员）"""
    if current_user.role != "admin":
        raise HTTPException(status_code=403, detail="无权限")
    config = await attendance_config_service.set_config(db, data.key, data.value)
    return ResponseModel(data=config, message="设置成功")


# ==================== 用户偏好 ====================

@router.get("/user-preference", response_model=ResponseModel[UserPreferenceResponse])
async def get_user_preference(
    db: AsyncSession = Depends(get_db),
    current_user: UserResponse = Depends(get_current_user)
):
    """获取当前用户偏好"""
    pref = await user_preference_service.get_or_create(db, current_user.id)
    return ResponseModel(data=pref)


@router.put("/user-preference", response_model=ResponseModel[UserPreferenceResponse])
async def update_user_preference(
    data: UserPreferenceUpdate,
    db: AsyncSession = Depends(get_db),
    current_user: UserResponse = Depends(get_current_user)
):
    """更新用户偏好"""
    pref = await user_preference_service.get_or_create(db, current_user.id)
    updated = await user_preference_service.update(db, pref.id, data.model_dump(exclude_unset=True, by_alias=False))
    return ResponseModel(data=updated, message="更新成功")


# ==================== 出差模板 ====================

@router.get("/trip-templates", response_model=ResponseModel[List[TripTemplateResponse]])
async def get_trip_templates(
    db: AsyncSession = Depends(get_db),
    current_user: UserResponse = Depends(get_current_user)
):
    """获取出差模板列表"""
    templates = await trip_template_service.find_by_user(db, current_user.id)
    return ResponseModel(data=templates)


@router.post("/trip-templates", response_model=ResponseModel[TripTemplateResponse])
async def create_trip_template(
    data: TripTemplateCreate,
    db: AsyncSession = Depends(get_db),
    current_user: UserResponse = Depends(get_current_user)
):
    """创建出差模板"""
    template = await trip_template_service.create(db, {**data.model_dump(by_alias=False), "user_id": current_user.id})
    return ResponseModel(data=template)


@router.put("/trip-templates/{template_id}", response_model=ResponseModel[TripTemplateResponse])
async def update_trip_template(
    template_id: int,
    data: TripTemplateUpdate,
    db: AsyncSession = Depends(get_db),
    current_user: UserResponse = Depends(get_current_user)
):
    """更新出差模板"""
    template = await trip_template_service.get_by_id(db, template_id)
    if not template:
        raise HTTPException(status_code=404, detail="模板不存在")
    if template.user_id != current_user.id:
        raise HTTPException(status_code=403, detail="无权限")
    updated = await trip_template_service.update(db, template_id, data.model_dump(exclude_unset=True, by_alias=False))
    return ResponseModel(data=updated)


@router.delete("/trip-templates/{template_id}")
async def delete_trip_template(
    template_id: int,
    db: AsyncSession = Depends(get_db),
    current_user: UserResponse = Depends(get_current_user)
):
    """删除出差模板"""
    template = await trip_template_service.get_by_id(db, template_id)
    if not template:
        raise HTTPException(status_code=404, detail="模板不存在")
    if template.user_id != current_user.id:
        raise HTTPException(status_code=403, detail="无权限")
    await trip_template_service.delete(db, template_id)
    return ResponseModel(message="删除成功")


# ==================== 城市配置 ====================

@router.get("/cities", response_model=ResponseModel[List[CityConfigResponse]])
async def get_city_configs(
    keyword: str = None,
    db: AsyncSession = Depends(get_db),
    current_user: UserResponse = Depends(get_current_user)
):
    """获取城市配置列表"""
    if keyword:
        cities = await city_config_service.search(db, keyword)
    else:
        cities = await city_config_service.get_all(db)
    return ResponseModel(data=cities)


@router.get("/cities/{city_id}", response_model=ResponseModel[CityConfigResponse])
async def get_city_config(
    city_id: int,
    db: AsyncSession = Depends(get_db),
    current_user: UserResponse = Depends(get_current_user)
):
    """获取城市配置详情"""
    city = await city_config_service.get_by_id(db, city_id)
    if not city:
        raise HTTPException(status_code=404, detail="城市不存在")
    return ResponseModel(data=city)


@router.post("/cities", response_model=ResponseModel[CityConfigResponse])
async def create_city_config(
    data: CityConfigCreate,
    db: AsyncSession = Depends(get_db),
    current_user: UserResponse = Depends(get_current_user)
):
    """创建城市配置（管理员）"""
    if current_user.role != "admin":
        raise HTTPException(status_code=403, detail="无权限")
    city = await city_config_service.create(db, data.model_dump(by_alias=False))
    return ResponseModel(data=city)


@router.put("/cities/{city_id}", response_model=ResponseModel[CityConfigResponse])
async def update_city_config(
    city_id: int,
    data: CityConfigUpdate,
    db: AsyncSession = Depends(get_db),
    current_user: UserResponse = Depends(get_current_user)
):
    """更新城市配置（管理员）"""
    if current_user.role != "admin":
        raise HTTPException(status_code=403, detail="无权限")
    city = await city_config_service.update(db, city_id, data.model_dump(exclude_unset=True, by_alias=False))
    if not city:
        raise HTTPException(status_code=404, detail="城市不存在")
    return ResponseModel(data=city)


@router.delete("/cities/{city_id}")
async def delete_city_config(
    city_id: int,
    db: AsyncSession = Depends(get_db),
    current_user: UserResponse = Depends(get_current_user)
):
    """删除城市配置（管理员）"""
    if current_user.role != "admin":
        raise HTTPException(status_code=403, detail="无权限")
    success = await city_config_service.delete(db, city_id)
    if not success:
        raise HTTPException(status_code=404, detail="城市不存在")
    return ResponseModel(message="删除成功")


# ==================== 节假日配置 ====================

@router.get("/holidays", response_model=ResponseModel[List[HolidayConfigResponse]])
async def get_holiday_configs(
    start_date: str = None,
    end_date: str = None,
    db: AsyncSession = Depends(get_db),
    current_user: UserResponse = Depends(get_current_user)
):
    """获取节假日配置列表"""
    if start_date and end_date:
        holidays = await holiday_config_service.get_by_date_range(db, start_date, end_date)
    else:
        holidays = await holiday_config_service.get_all(db)
    return ResponseModel(data=holidays)


@router.get("/holidays/check", response_model=ResponseModel[dict])
async def check_workday(
    date: str,
    db: AsyncSession = Depends(get_db),
    current_user: UserResponse = Depends(get_current_user)
):
    """检查是否为工作日"""
    is_workday = await holiday_config_service.is_workday(db, date)
    holiday = await holiday_config_service.get_by_date(db, date)
    return ResponseModel(data={
        "date": date,
        "isWorkday": is_workday,
        "holidayName": holiday.name if holiday else None,
        "type": holiday.type if holiday else ("workday" if is_workday else "weekend")
    })


@router.post("/holidays", response_model=ResponseModel[HolidayConfigResponse])
async def create_holiday_config(
    data: HolidayConfigCreate,
    db: AsyncSession = Depends(get_db),
    current_user: UserResponse = Depends(get_current_user)
):
    """创建节假日配置（管理员）"""
    if current_user.role != "admin":
        raise HTTPException(status_code=403, detail="无权限")
    holiday = await holiday_config_service.create(db, data.model_dump(by_alias=False))
    return ResponseModel(data=holiday)


@router.put("/holidays/{holiday_id}", response_model=ResponseModel[HolidayConfigResponse])
async def update_holiday_config(
    holiday_id: int,
    data: HolidayConfigUpdate,
    db: AsyncSession = Depends(get_db),
    current_user: UserResponse = Depends(get_current_user)
):
    """更新节假日配置（管理员）"""
    if current_user.role != "admin":
        raise HTTPException(status_code=403, detail="无权限")
    holiday = await holiday_config_service.update(db, holiday_id, data.model_dump(exclude_unset=True, by_alias=False))
    if not holiday:
        raise HTTPException(status_code=404, detail="节假日配置不存在")
    return ResponseModel(data=holiday)


@router.delete("/holidays/{holiday_id}")
async def delete_holiday_config(
    holiday_id: int,
    db: AsyncSession = Depends(get_db),
    current_user: UserResponse = Depends(get_current_user)
):
    """删除节假日配置（管理员）"""
    if current_user.role != "admin":
        raise HTTPException(status_code=403, detail="无权限")
    success = await holiday_config_service.delete(db, holiday_id)
    if not success:
        raise HTTPException(status_code=404, detail="节假日配置不存在")
    return ResponseModel(message="删除成功")
