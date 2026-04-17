"""
预定服务
"""
from typing import Optional, List
from datetime import datetime
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from app.models import Reservation
from app.services.base import BaseService


class ReservationService(BaseService[Reservation]):
    """预定服务"""

    def __init__(self):
        super().__init__(Reservation)

    async def find_by_user(self, db: AsyncSession, user_id: int) -> List[Reservation]:
        """查询用户预定"""
        result = await db.execute(
            select(Reservation).where(Reservation.userId == user_id).order_by(Reservation.start.desc())
        )
        return result.scalars().all()

    async def find_by_room(self, db: AsyncSession, room_id: int) -> List[Reservation]:
        """查询会议室预定"""
        result = await db.execute(
            select(Reservation).where(Reservation.roomId == room_id).order_by(Reservation.start)
        )
        return result.scalars().all()

    async def find_by_room_and_date(self, db: AsyncSession, room_id: int, date: str) -> List[Reservation]:
        """查询指定日期的预定"""
        result = await db.execute(
            select(Reservation).where(
                Reservation.roomId == room_id,
                Reservation.start.like(f"{date}%")
            ).order_by(Reservation.start)
        )
        return result.scalars().all()

    async def check_conflict(
        self, db: AsyncSession, room_id: int, start: str, end: str, exclude_id: int = None
    ) -> Optional[Reservation]:
        """检查预定冲突"""
        date = start.split(" ")[0]
        reservations = await self.find_by_room_and_date(db, room_id, date)

        start_dt = datetime.strptime(start, "%Y-%m-%d %H:%M")
        end_dt = datetime.strptime(end, "%Y-%m-%d %H:%M")

        for r in reservations:
            if exclude_id and r.id == exclude_id:
                continue

            r_start = datetime.strptime(r.start, "%Y-%m-%d %H:%M")
            r_end = datetime.strptime(r.end, "%Y-%m-%d %H:%M")

            # 时间重叠检测
            if start_dt < r_end and end_dt > r_start:
                return r

        return None

    async def get_future_reservations(self, db: AsyncSession, user_id: int) -> List[Reservation]:
        """获取用户未来的预定"""
        now = datetime.now().strftime("%Y-%m-%d %H:%M")
        result = await db.execute(
            select(Reservation).where(
                Reservation.userId == user_id,
                Reservation.start >= now
            ).order_by(Reservation.start)
        )
        return result.scalars().all()


reservation_service = ReservationService()