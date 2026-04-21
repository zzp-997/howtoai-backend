"""
公告通知服务
"""
from typing import List, Optional
import json
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from app.models import Announcement
from app.services.base import BaseService


class AnnouncementService(BaseService[Announcement]):
    """公告通知服务"""

    def __init__(self):
        super().__init__(Announcement)

    async def find_all_ordered(self, db: AsyncSession) -> List[Announcement]:
        """查询所有公告（置顶优先）"""
        result = await db.execute(
            select(Announcement).order_by(Announcement.is_top.desc(), Announcement.publish_time.desc())
        )
        return result.scalars().all()

    async def find_by_category(self, db: AsyncSession, category: str) -> List[Announcement]:
        """按分类查询"""
        result = await db.execute(
            select(Announcement).where(Announcement.category == category)
            .order_by(Announcement.is_top.desc(), Announcement.publish_time.desc())
        )
        return result.scalars().all()

    async def find_unread(self, db: AsyncSession, user_id: int) -> List[Announcement]:
        """查询未读公告"""
        all_announcements = await self.find_all_ordered(db)
        return [a for a in all_announcements if user_id not in self._get_read_list(a.read_by)]

    async def mark_as_read(self, db: AsyncSession, id: int, user_id: int) -> Optional[Announcement]:
        """标记已读"""
        announcement = await self.get_by_id(db, id)
        if not announcement:
            return None

        read_list = self._get_read_list(announcement.read_by)
        if user_id not in read_list:
            read_list.append(user_id)
            return await self.update(db, id, {"read_by": json.dumps(read_list)})
        return announcement

    async def get_unread_count(self, db: AsyncSession, user_id: int) -> int:
        """获取未读数量"""
        all_announcements = await self.get_all(db)
        return len([a for a in all_announcements if user_id not in self._get_read_list(a.read_by)])

    def _get_read_list(self, read_by: str) -> List[int]:
        """解析已读列表"""
        if not read_by:
            return []
        try:
            return json.loads(read_by)
        except:
            return []


announcement_service = AnnouncementService()
