"""
报销单服务
"""
from typing import List, Optional
import json
from datetime import datetime
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from app.models import ExpenseClaim
from app.services.base import BaseService


class ExpenseClaimService(BaseService[ExpenseClaim]):
    """报销单服务"""

    def __init__(self):
        super().__init__(ExpenseClaim)

    async def find_by_user(self, db: AsyncSession, user_id: int) -> List[ExpenseClaim]:
        """查询用户报销单"""
        result = await db.execute(
            select(ExpenseClaim).where(ExpenseClaim.userId == user_id).order_by(ExpenseClaim.createdAt.desc())
        )
        return result.scalars().all()

    async def find_by_trip(self, db: AsyncSession, trip_id: int) -> Optional[ExpenseClaim]:
        """按差旅ID查询"""
        result = await db.execute(
            select(ExpenseClaim).where(ExpenseClaim.tripId == trip_id)
        )
        return result.scalar_one_or_none()

    async def find_by_status(self, db: AsyncSession, status: str) -> List[ExpenseClaim]:
        """按状态查询"""
        result = await db.execute(
            select(ExpenseClaim).where(ExpenseClaim.status == status).order_by(ExpenseClaim.createdAt.desc())
        )
        return result.scalars().all()

    async def submit(self, db: AsyncSession, id: int) -> Optional[ExpenseClaim]:
        """提交报销单"""
        return await self.update(db, id, {
            "status": "submitted",
            "submittedAt": datetime.now(),
            "updatedAt": datetime.now()
        })

    async def approve(self, db: AsyncSession, id: int, approver_id: int) -> Optional[ExpenseClaim]:
        """审批报销单"""
        return await self.update(db, id, {
            "status": "approved",
            "approvedBy": approver_id,
            "approvedAt": datetime.now(),
            "updatedAt": datetime.now()
        })


expense_claim_service = ExpenseClaimService()