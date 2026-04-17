"""
会议室服务
"""
from typing import Optional, List
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from app.models import MeetingRoom
from app.services.base import BaseService


class MeetingRoomService(BaseService[MeetingRoom]):
    """会议室服务"""

    def __init__(self):
        super().__init__(MeetingRoom)

    async def search_by_name(self, db: AsyncSession, keyword: str) -> List[MeetingRoom]:
        """按名称搜索"""
        query = select(MeetingRoom)
        if keyword:
            query = query.where(MeetingRoom.name.ilike(f"%{keyword}%"))
        result = await db.execute(query)
        return result.scalars().all()

    async def find_by_capacity(self, db: AsyncSession, min_capacity: int) -> List[MeetingRoom]:
        """按容量筛选"""
        result = await db.execute(
            select(MeetingRoom).where(MeetingRoom.capacity >= min_capacity)
        )
        return result.scalars().all()

    async def get_active_rooms(self, db: AsyncSession) -> List[MeetingRoom]:
        """获取所有启用的会议室"""
        result = await db.execute(
            select(MeetingRoom).where(MeetingRoom.isActive == True)
        )
        return result.scalars().all()


meeting_room_service = MeetingRoomService()