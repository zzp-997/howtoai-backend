"""
差旅申请服务
"""
from typing import List, Optional
from datetime import datetime
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from app.models import Trip
from app.services.base import BaseService


class TripService(BaseService[Trip]):
    """差旅申请服务"""

    def __init__(self):
        super().__init__(Trip)

    async def find_by_user(self, db: AsyncSession, user_id: int) -> List[Trip]:
        """查询用户差旅申请"""
        result = await db.execute(
            select(Trip).where(Trip.userId == user_id).order_by(Trip.createdAt.desc())
        )
        return result.scalars().all()

    async def find_by_status(self, db: AsyncSession, status: str) -> List[Trip]:
        """按状态查询"""
        result = await db.execute(
            select(Trip).where(Trip.status == status).order_by(Trip.createdAt.desc())
        )
        return result.scalars().all()

    async def find_pending(self, db: AsyncSession) -> List[Trip]:
        """查询待审批"""
        return await self.find_by_status(db, "pending")

    async def approve(
        self, db: AsyncSession, id: int, approved: bool, comment: str, approver_id: int
    ) -> Optional[Trip]:
        """审批差旅申请"""
        return await self.update(db, id, {
            "status": "approved" if approved else "rejected",
            "approvalComment": comment,
            "approvedBy": approver_id,
            "approvedAt": datetime.now()
        })

    async def calculate_total_fee(self, db: AsyncSession, status: str = None) -> dict:
        """统计差旅费用"""
        query = select(Trip)
        if status:
            query = query.where(Trip.status == status)
        result = await db.execute(query)
        trips = result.scalars().all()

        total_transport = sum(t.estTransportFee or 0 for t in trips)
        total_accom = sum(t.estAccomFee or 0 for t in trips)

        return {
            "count": len(trips),
            "totalTransport": total_transport,
            "totalAccom": total_accom,
            "total": total_transport + total_accom
        }


trip_service = TripService()