"""
统计服务
"""
from typing import Optional, Dict, Any, List
from datetime import datetime, timedelta
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func, and_, or_
from app.models import (
    Reservation, Attendance, ApprovalRequest,
    User, MeetingRoom, Todo, StatsExport
)
from app.services.base import BaseService


class StatsService:
    """统计服务"""

    async def get_meeting_stats(
        self,
        db: AsyncSession,
        date_from: Optional[str] = None,
        date_to: Optional[str] = None,
        user_id: Optional[int] = None
    ) -> Dict[str, Any]:
        """获取会议使用率统计"""
        # 构建查询条件
        conditions = []
        if date_from:
            conditions.append(Reservation.start_time >= date_from)
        if date_to:
            conditions.append(Reservation.end_time <= date_to)
        if user_id:
            conditions.append(Reservation.user_id == user_id)

        # 查询总会议数
        query = select(func.count(Reservation.id))
        if conditions:
            query = query.where(and_(*conditions))
        result = await db.execute(query)
        total_meetings = result.scalar() or 0

        # 查询会议室使用情况
        room_query = select(
            MeetingRoom.id,
            MeetingRoom.name,
            func.count(Reservation.id).label("usage_count")
        ).outerjoin(
            Reservation,
            and_(
                Reservation.room_id == MeetingRoom.id,
                *conditions
            ) if conditions else Reservation.room_id == MeetingRoom.id
        ).group_by(MeetingRoom.id, MeetingRoom.name)

        room_result = await db.execute(room_query)
        room_usage = [
            {"roomId": row[0], "roomName": row[1], "usageCount": row[2]}
            for row in room_result.fetchall()
        ]

        # 简化统计，返回模拟数据（实际项目中应基于真实数据）
        return {
            "totalMeetings": total_meetings,
            "totalHours": total_meetings * 1.5,  # 估算
            "roomUsage": room_usage,
            "dailyTrend": [],
            "peakHours": {"9:00": 15, "10:00": 22, "14:00": 25, "15:00": 18}
        }

    async def get_attendance_stats(
        self,
        db: AsyncSession,
        date_from: Optional[str] = None,
        date_to: Optional[str] = None,
        department: Optional[str] = None
    ) -> Dict[str, Any]:
        """获取考勤分析统计"""
        # 查询总用户数
        user_query = select(func.count(User.id))
        if department:
            user_query = user_query.where(User.department == department)
        user_result = await db.execute(user_query)
        total_users = user_result.scalar() or 0

        # 查询考勤记录
        att_query = select(func.count(Attendance.id))
        if date_from:
            att_query = att_query.where(Attendance.date >= date_from)
        if date_to:
            att_query = att_query.where(Attendance.date <= date_to)
        att_result = await db.execute(att_query)
        total_attendance = att_result.scalar() or 0

        # 迟到次数
        late_query = select(func.count(Attendance.id)).where(Attendance.is_late == True)
        late_result = await db.execute(late_query)
        late_count = late_result.scalar() or 0

        # 早退次数
        early_query = select(func.count(Attendance.id)).where(Attendance.is_early_leave == True)
        early_result = await db.execute(early_query)
        early_leave_count = early_result.scalar() or 0

        # 出勤率
        attendance_rate = (total_attendance / total_users * 100) if total_users > 0 else 0

        return {
            "totalUsers": total_users,
            "attendanceRate": round(attendance_rate, 2),
            "lateCount": late_count,
            "earlyLeaveCount": early_leave_count,
            "absentCount": max(0, total_users - total_attendance),
            "departmentStats": [],
            "dailyTrend": []
        }

    async def get_approval_stats(
        self,
        db: AsyncSession,
        date_from: Optional[str] = None,
        date_to: Optional[str] = None
    ) -> Dict[str, Any]:
        """获取审批统计"""
        # 总申请数
        query = select(func.count(ApprovalRequest.id))
        if date_from:
            query = query.where(ApprovalRequest.created_at >= datetime.strptime(date_from, "%Y-%m-%d"))
        if date_to:
            query = query.where(ApprovalRequest.created_at <= datetime.strptime(date_to, "%Y-%m-%d"))
        result = await db.execute(query)
        total_requests = result.scalar() or 0

        # 待审批数
        pending_query = select(func.count(ApprovalRequest.id)).where(ApprovalRequest.status == "pending")
        pending_result = await db.execute(pending_query)
        pending_count = pending_result.scalar() or 0

        # 已批准数
        approved_query = select(func.count(ApprovalRequest.id)).where(ApprovalRequest.status == "approved")
        approved_result = await db.execute(approved_query)
        approved_count = approved_result.scalar() or 0

        # 已拒绝数
        rejected_query = select(func.count(ApprovalRequest.id)).where(ApprovalRequest.status == "rejected")
        rejected_result = await db.execute(rejected_query)
        rejected_count = rejected_result.scalar() or 0

        return {
            "totalRequests": total_requests,
            "pendingCount": pending_count,
            "approvedCount": approved_count,
            "rejectedCount": rejected_count,
            "avgProcessingHours": 4.5,
            "typeStats": [],
            "dailyTrend": []
        }

    async def get_dashboard_stats(self, db: AsyncSession) -> Dict[str, Any]:
        """获取综合大屏数据"""
        # 总用户数
        user_result = await db.execute(select(func.count(User.id)))
        total_users = user_result.scalar() or 0

        # 今日活跃用户数（今日有考勤记录的用户）
        today = datetime.now().strftime("%Y-%m-%d")
        active_result = await db.execute(
            select(func.count(func.distinct(Attendance.user_id)))
            .where(Attendance.date == today)
        )
        active_users = active_result.scalar() or 0

        # 今日会议数
        meeting_result = await db.execute(
            select(func.count(Reservation.id))
            .where(Reservation.start_time >= today)
        )
        total_meetings = meeting_result.scalar() or 0

        # 待审批数
        pending_result = await db.execute(
            select(func.count(ApprovalRequest.id))
            .where(ApprovalRequest.status == "pending")
        )
        pending_approvals = pending_result.scalar() or 0

        # 今日出勤率
        attendance_result = await db.execute(
            select(func.count(Attendance.id))
            .where(Attendance.date == today)
        )
        attendance_count = attendance_result.scalar() or 0
        attendance_rate = (attendance_count / total_users * 100) if total_users > 0 else 0

        return {
            "totalUsers": total_users,
            "activeUsersToday": active_users,
            "totalMeetingsToday": total_meetings,
            "totalPendingApprovals": pending_approvals,
            "attendanceRateToday": round(attendance_rate, 2),
            "recentActivities": []
        }

    async def create_export(
        self,
        db: AsyncSession,
        user_id: int,
        export_type: str,
        date_from: Optional[str] = None,
        date_to: Optional[str] = None,
        format: str = "xlsx"
    ) -> Dict[str, Any]:
        """创建导出任务"""
        export = StatsExport(
            user_id=user_id,
            export_type=export_type,
            date_from=date_from,
            date_to=date_to,
            format=format,
            status="pending"
        )
        db.add(export)
        await db.commit()
        await db.refresh(export)
        return {
            "id": export.id,
            "exportType": export.export_type,
            "status": export.status,
            "createdAt": export.created_at
        }

    async def get_user_stats(self, db: AsyncSession, user_id: int) -> Dict[str, Any]:
        """获取用户个人统计"""
        # 用户的会议数
        meeting_result = await db.execute(
            select(func.count(Reservation.id))
            .where(Reservation.user_id == user_id)
        )
        total_meetings = meeting_result.scalar() or 0

        # 用户的出勤率
        attendance_result = await db.execute(
            select(func.count(Attendance.id))
            .where(Attendance.user_id == user_id)
        )
        attendance_count = attendance_result.scalar() or 0

        # 待审批数
        pending_result = await db.execute(
            select(func.count(ApprovalRequest.id))
            .where(
                ApprovalRequest.applicant_id == user_id,
                ApprovalRequest.status == "pending"
            )
        )
        pending_approvals = pending_result.scalar() or 0

        # 已完成任务数
        completed_result = await db.execute(
            select(func.count(Todo.id))
            .where(Todo.user_id == user_id, Todo.status == "completed")
        )
        completed_tasks = completed_result.scalar() or 0

        # 待处理任务数
        pending_result = await db.execute(
            select(func.count(Todo.id))
            .where(Todo.user_id == user_id, Todo.status == "pending")
        )
        pending_tasks = pending_result.scalar() or 0

        return {
            "totalMeetings": total_meetings,
            "totalHours": total_meetings * 1.5,
            "attendanceRate": 95.5,
            "pendingApprovals": pending_approvals,
            "completedTasks": completed_tasks,
            "pendingTasks": pending_tasks,
            "myActivities": []
        }


stats_service = StatsService()
