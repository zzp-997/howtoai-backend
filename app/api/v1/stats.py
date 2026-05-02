"""
数据统计 API
"""
from fastapi import APIRouter, Depends, Query
from sqlalchemy.ext.asyncio import AsyncSession
from typing import Optional
from app.core.database import get_db
from app.schemas.common import ResponseModel
from app.schemas.stats import (
    MeetingStatsResponse, AttendanceStatsResponse, ApprovalStatsResponse,
    DashboardStatsResponse, ExportRequest, ExportResponse, UserStatsResponse
)
from app.services.stats_service import stats_service
from app.api.v1.auth import get_current_user
from app.schemas.user import UserResponse

router = APIRouter(prefix="/stats", tags=["数据统计"])


@router.get("/meetings", response_model=ResponseModel[MeetingStatsResponse])
async def get_meeting_stats(
    period: Optional[str] = Query(None, description="时间维度"),
    startDate: Optional[str] = Query(None, description="开始日期"),
    endDate: Optional[str] = Query(None, description="结束日期"),
    db: AsyncSession = Depends(get_db),
    current_user: UserResponse = Depends(get_current_user)
):
    """获取会议使用率统计"""
    stats = await stats_service.get_meeting_stats(
        db, date_from=startDate, date_to=endDate, user_id=current_user.id
    )
    return ResponseModel(code=200, message="success", data=stats)


@router.get("/attendance", response_model=ResponseModel[AttendanceStatsResponse])
async def get_attendance_stats(
    period: Optional[str] = Query(None, description="时间维度"),
    startDate: Optional[str] = Query(None, description="开始日期"),
    endDate: Optional[str] = Query(None, description="结束日期"),
    department: Optional[str] = Query(None, description="部门"),
    db: AsyncSession = Depends(get_db),
    current_user: UserResponse = Depends(get_current_user)
):
    """获取考勤分析统计"""
    stats = await stats_service.get_attendance_stats(
        db, date_from=startDate, date_to=endDate, department=department
    )
    return ResponseModel(code=200, message="success", data=stats)


@router.get("/approvals", response_model=ResponseModel[ApprovalStatsResponse])
async def get_approval_stats(
    period: Optional[str] = Query(None, description="时间维度"),
    startDate: Optional[str] = Query(None, description="开始日期"),
    endDate: Optional[str] = Query(None, description="结束日期"),
    db: AsyncSession = Depends(get_db),
    current_user: UserResponse = Depends(get_current_user)
):
    """获取审批统计"""
    stats = await stats_service.get_approval_stats(
        db, date_from=startDate, date_to=endDate
    )
    return ResponseModel(code=200, message="success", data=stats)


@router.get("/dashboard", response_model=ResponseModel[DashboardStatsResponse])
async def get_dashboard_stats(
    db: AsyncSession = Depends(get_db),
    current_user: UserResponse = Depends(get_current_user)
):
    """获取综合大屏数据"""
    stats = await stats_service.get_dashboard_stats(db)
    return ResponseModel(code=200, message="success", data=stats)


@router.post("/export", response_model=ResponseModel[ExportResponse])
async def export_report(
    export_data: ExportRequest,
    db: AsyncSession = Depends(get_db),
    current_user: UserResponse = Depends(get_current_user)
):
    """创建导出任务"""
    export = await stats_service.create_export(
        db,
        user_id=current_user.id,
        export_type=export_data.export_type,
        date_from=export_data.date_from,
        date_to=export_data.date_to,
        format=export_data.format
    )
    return ResponseModel(code=200, message="创建导出任务成功", data=export)


@router.get("/me", response_model=ResponseModel[UserStatsResponse])
async def get_my_stats(
    db: AsyncSession = Depends(get_db),
    current_user: UserResponse = Depends(get_current_user)
):
    """获取用户个人统计"""
    stats = await stats_service.get_user_stats(db, current_user.id)
    return ResponseModel(code=200, message="success", data=stats)
