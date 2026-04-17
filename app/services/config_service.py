"""
配置相关服务
"""
from typing import List, Optional
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from app.services.base import BaseService
from app.models.models import (
    AttendanceConfig, UserPreference, TripTemplate,
    CityConfig, HolidayConfig
)


class AttendanceConfigService(BaseService[AttendanceConfig]):
    """考勤配置服务"""

    def __init__(self):
        super().__init__(AttendanceConfig)

    async def get_by_key(self, db: AsyncSession, key: str) -> Optional[AttendanceConfig]:
        """根据 key 查询"""
        result = await db.execute(
            select(AttendanceConfig).where(AttendanceConfig.key == key)
        )
        return result.scalar_one_or_none()

    async def set_config(self, db: AsyncSession, key: str, value: str) -> AttendanceConfig:
        """设置配置（存在则更新，不存在则创建）"""
        config = await self.get_by_key(db, key)
        if config:
            config.value = value
            await db.commit()
            await db.refresh(config)
            return config
        else:
            return await self.create(db, {"key": key, "value": value})

    async def get_all_as_dict(self, db: AsyncSession) -> dict:
        """获取所有配置为字典"""
        configs = await self.get_all(db)
        return {c.key: c.value for c in configs}


class UserPreferenceService(BaseService[UserPreference]):
    """用户偏好服务"""

    def __init__(self):
        super().__init__(UserPreference)

    async def get_by_user_id(self, db: AsyncSession, user_id: int) -> Optional[UserPreference]:
        """根据用户 ID 查询"""
        result = await db.execute(
            select(UserPreference).where(UserPreference.userId == user_id)
        )
        return result.scalar_one_or_none()

    async def get_or_create(self, db: AsyncSession, user_id: int) -> UserPreference:
        """获取或创建用户偏好"""
        pref = await self.get_by_user_id(db, user_id)
        if not pref:
            pref = await self.create(db, {"userId": user_id})
        return pref


class TripTemplateService(BaseService[TripTemplate]):
    """出差模板服务"""

    def __init__(self):
        super().__init__(TripTemplate)

    async def find_by_user(self, db: AsyncSession, user_id: int) -> List[TripTemplate]:
        """根据用户 ID 查询"""
        result = await db.execute(
            select(TripTemplate)
            .where(TripTemplate.userId == user_id)
            .order_by(TripTemplate.useCount.desc())
        )
        return result.scalars().all()

    async def increment_use(self, db: AsyncSession, template_id: int) -> Optional[TripTemplate]:
        """增加使用次数"""
        from datetime import datetime
        template = await self.get_by_id(db, template_id)
        if template:
            template.useCount += 1
            template.lastUsedAt = datetime.now()
            await db.commit()
            await db.refresh(template)
        return template


class CityConfigService(BaseService[CityConfig]):
    """城市配置服务"""

    def __init__(self):
        super().__init__(CityConfig)

    async def search(self, db: AsyncSession, keyword: str) -> List[CityConfig]:
        """搜索城市"""
        result = await db.execute(
            select(CityConfig)
            .where(CityConfig.name.ilike(f"%{keyword}%"))
        )
        return result.scalars().all()

    async def get_by_name(self, db: AsyncSession, name: str) -> Optional[CityConfig]:
        """根据名称查询"""
        result = await db.execute(
            select(CityConfig).where(CityConfig.name == name)
        )
        return result.scalar_one_or_none()


class HolidayConfigService(BaseService[HolidayConfig]):
    """节假日配置服务"""

    def __init__(self):
        super().__init__(HolidayConfig)

    async def get_by_date(self, db: AsyncSession, date: str) -> Optional[HolidayConfig]:
        """根据日期查询"""
        result = await db.execute(
            select(HolidayConfig).where(HolidayConfig.date == date)
        )
        return result.scalar_one_or_none()

    async def get_by_date_range(self, db: AsyncSession, start_date: str, end_date: str) -> List[HolidayConfig]:
        """根据日期范围查询"""
        result = await db.execute(
            select(HolidayConfig)
            .where(HolidayConfig.date >= start_date)
            .where(HolidayConfig.date <= end_date)
            .order_by(HolidayConfig.date)
        )
        return result.scalars().all()

    async def is_workday(self, db: AsyncSession, date: str) -> bool:
        """判断是否为工作日"""
        holiday = await self.get_by_date(db, date)
        if holiday:
            return holiday.type == "workday"
        # 未配置的日期，按周末判断
        from datetime import datetime
        d = datetime.strptime(date, "%Y-%m-%d")
        return d.weekday() < 5  # 0-4 为工作日


# 创建服务实例
attendance_config_service = AttendanceConfigService()
user_preference_service = UserPreferenceService()
trip_template_service = TripTemplateService()
city_config_service = CityConfigService()
holiday_config_service = HolidayConfigService()
