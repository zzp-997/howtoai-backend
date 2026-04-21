"""
请假申请服务
"""
from typing import List, Optional
from datetime import datetime
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from app.models import Leave
from app.services.base import BaseService


class LeaveService(BaseService[Leave]):
    """请假申请服务"""

    def __init__(self):
        super().__init__(Leave)

    async def find_by_user(self, db: AsyncSession, user_id: int) -> List[Leave]:
        """查询用户请假申请"""
        result = await db.execute(
            select(Leave).where(Leave.user_id == user_id).order_by(Leave.created_at.desc())
        )
        return result.scalars().all()

    async def find_by_status(self, db: AsyncSession, status: str) -> List[Leave]:
        """按状态查询"""
        result = await db.execute(
            select(Leave).where(Leave.status == status).order_by(Leave.created_at.desc())
        )
        return result.scalars().all()

    async def find_pending(self, db: AsyncSession) -> List[Leave]:
        """查询待审批"""
        return await self.find_by_status(db, "pending")

    async def approve(
        self, db: AsyncSession, id: int, approved: bool, comment: str, approver_id: int
    ) -> Optional[Leave]:
        """审批请假申请"""
        return await self.update(db, id, {
            "status": "approved" if approved else "rejected",
            "approval_comment": comment,
            "approved_by": approver_id,
            "approved_at": datetime.now()
        })

    async def check_overlap(
        self, db: AsyncSession, user_id: int, start_date: str, end_date: str, exclude_id: int = None
    ) -> Optional[Leave]:
        """检查日期重叠"""
        leaves = await self.find_by_user(db, user_id)

        for leave in leaves:
            if exclude_id and leave.id == exclude_id:
                continue
            if leave.status == "rejected":
                continue

            # 检查日期重叠
            if start_date <= leave.end_date and end_date >= leave.start_date:
                return leave

        return None


leave_service = LeaveService()
