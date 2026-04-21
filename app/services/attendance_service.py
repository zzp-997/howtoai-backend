"""
考勤服务
"""
from typing import List, Optional
from datetime import datetime
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, and_
from app.models import Attendance, MakeUpRequest
from app.services.base import BaseService


class AttendanceService(BaseService[Attendance]):
    """考勤服务"""

    def __init__(self):
        super().__init__(Attendance)

    async def find_by_user(self, db: AsyncSession, user_id: int) -> List[Attendance]:
        """查询用户考勤记录"""
        result = await db.execute(
            select(Attendance).where(Attendance.user_id == user_id).order_by(Attendance.date.desc())
        )
        return result.scalars().all()

    async def find_by_user_and_date(self, db: AsyncSession, user_id: int, date: str) -> Optional[Attendance]:
        """查询用户指定日期的记录"""
        result = await db.execute(
            select(Attendance).where(
                and_(Attendance.user_id == user_id, Attendance.date == date)
            )
        )
        return result.scalar_one_or_none()

    async def find_by_user_and_month(self, db: AsyncSession, user_id: int, month: str) -> List[Attendance]:
        """查询用户指定月份的记录"""
        result = await db.execute(
            select(Attendance).where(
                Attendance.user_id == user_id,
                Attendance.date.like(f"{month}%")
            ).order_by(Attendance.date)
        )
        return result.scalars().all()

    async def check_in(self, db: AsyncSession, user_id: int, work_start: str = "09:00") -> Attendance:
        """上班打卡"""
        today = datetime.now().strftime("%Y-%m-%d")
        now = datetime.now().strftime("%H:%M")

        existing = await self.find_by_user_and_date(db, user_id, today)
        if existing and existing.check_in_time:
            raise ValueError("今日已上班打卡")

        is_late = now > work_start

        if existing:
            return await self.update(db, existing.id, {"check_in_time": now, "is_late": is_late})
        else:
            return await self.create(db, {
                "user_id": user_id,
                "date": today,
                "check_in_time": now,
                "is_late": is_late,
                "status": "normal"
            })

    async def check_out(self, db: AsyncSession, user_id: int, work_end: str = "18:00") -> Attendance:
        """下班打卡"""
        today = datetime.now().strftime("%Y-%m-%d")
        now = datetime.now().strftime("%H:%M")

        existing = await self.find_by_user_and_date(db, user_id, today)
        if not existing:
            raise ValueError("请先上班打卡")
        if existing.check_out_time:
            raise ValueError("今日已下班打卡")

        is_early = now < work_end

        return await self.update(db, existing.id, {"check_out_time": now, "is_early_leave": is_early})

    async def get_monthly_stats(self, db: AsyncSession, user_id: int, month: str) -> dict:
        """获取用户本月统计"""
        records = await self.find_by_user_and_month(db, user_id, month)

        return {
            "total": len(records),
            "normal": len([r for r in records if r.check_in_time and r.check_out_time and not r.is_late]),
            "late": len([r for r in records if r.is_late]),
            "missingCheckIn": len([r for r in records if not r.check_in_time]),
            "missingCheckOut": len([r for r in records if not r.check_out_time])
        }


class MakeUpRequestService(BaseService[MakeUpRequest]):
    """补卡申请服务"""

    def __init__(self):
        super().__init__(MakeUpRequest)

    async def find_by_user(self, db: AsyncSession, user_id: int) -> List[MakeUpRequest]:
        """查询用户补卡申请"""
        result = await db.execute(
            select(MakeUpRequest).where(MakeUpRequest.user_id == user_id).order_by(MakeUpRequest.created_at.desc())
        )
        return result.scalars().all()

    async def find_pending(self, db: AsyncSession) -> List[MakeUpRequest]:
        """查询待审批"""
        result = await db.execute(
            select(MakeUpRequest).where(MakeUpRequest.status == "pending").order_by(MakeUpRequest.created_at.desc())
        )
        return result.scalars().all()

    async def approve(self, db: AsyncSession, id: int, approved: bool, approver_id: int) -> Optional[MakeUpRequest]:
        """审批补卡申请"""
        return await self.update(db, id, {
            "status": "approved" if approved else "rejected",
            "approved_by": approver_id,
            "approved_at": datetime.now()
        })


attendance_service = AttendanceService()
makeup_request_service = MakeUpRequestService()
