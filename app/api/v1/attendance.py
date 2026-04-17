"""
考勤打卡 API
"""
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from typing import List
from app.core.database import get_db
from app.schemas import (
    AttendanceResponse, AttendanceStats, MakeUpRequestCreate, MakeUpRequestResponse, ResponseModel
)
from app.services import attendance_service, makeup_request_service
from app.api.v1.auth import get_current_user
from app.schemas.user import UserResponse

router = APIRouter(prefix="/attendance", tags=["考勤打卡"])


# ==================== 考勤打卡 ====================

@router.get("", response_model=ResponseModel[List[AttendanceResponse]])
async def get_attendance_list(
    month: str = None,
    db: AsyncSession = Depends(get_db),
    current_user: UserResponse = Depends(get_current_user)
):
    """获取考勤记录"""
    if month:
        records = await attendance_service.find_by_user_and_month(db, current_user.id, month)
    else:
        records = await attendance_service.find_by_user(db, current_user.id)
    return ResponseModel(data=records)


@router.get("/today", response_model=ResponseModel[AttendanceResponse])
async def get_today_attendance(
    db: AsyncSession = Depends(get_db),
    current_user: UserResponse = Depends(get_current_user)
):
    """获取今日考勤"""
    from datetime import datetime
    today = datetime.now().strftime("%Y-%m-%d")
    record = await attendance_service.find_by_user_and_date(db, current_user.id, today)
    return ResponseModel(data=record)


@router.post("/check-in", response_model=ResponseModel[AttendanceResponse])
async def check_in(
    db: AsyncSession = Depends(get_db),
    current_user: UserResponse = Depends(get_current_user)
):
    """上班打卡"""
    try:
        record = await attendance_service.check_in(db, current_user.id)
        return ResponseModel(data=record, message="打卡成功")
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))


@router.post("/check-out", response_model=ResponseModel[AttendanceResponse])
async def check_out(
    db: AsyncSession = Depends(get_db),
    current_user: UserResponse = Depends(get_current_user)
):
    """下班打卡"""
    try:
        record = await attendance_service.check_out(db, current_user.id)
        return ResponseModel(data=record, message="打卡成功")
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))


@router.get("/stats", response_model=ResponseModel[AttendanceStats])
async def get_attendance_stats(
    month: str = None,
    db: AsyncSession = Depends(get_db),
    current_user: UserResponse = Depends(get_current_user)
):
    """获取考勤统计"""
    from datetime import datetime
    if not month:
        month = datetime.now().strftime("%Y-%m")
    stats = await attendance_service.get_monthly_stats(db, current_user.id, month)
    return ResponseModel(data=stats)


# ==================== 补卡申请 ====================

@router.get("/makeup-requests", response_model=ResponseModel[List[MakeUpRequestResponse]])
async def get_makeup_requests(
    db: AsyncSession = Depends(get_db),
    current_user: UserResponse = Depends(get_current_user)
):
    """获取补卡申请列表"""
    if current_user.role == "admin":
        requests = await makeup_request_service.find_pending(db)
    else:
        requests = await makeup_request_service.find_by_user(db, current_user.id)
    return ResponseModel(data=requests)


@router.post("/makeup-requests", response_model=ResponseModel[MakeUpRequestResponse])
async def create_makeup_request(
    data: MakeUpRequestCreate,
    db: AsyncSession = Depends(get_db),
    current_user: UserResponse = Depends(get_current_user)
):
    """创建补卡申请"""
    request = await makeup_request_service.create(db, {**data.model_dump(), "userId": current_user.id})
    return ResponseModel(data=request)


@router.post("/makeup-requests/{request_id}/approve", response_model=ResponseModel[MakeUpRequestResponse])
async def approve_makeup_request(
    request_id: int,
    approved: bool,
    db: AsyncSession = Depends(get_db),
    current_user: UserResponse = Depends(get_current_user)
):
    """审批补卡申请（管理员）"""
    if current_user.role != "admin":
        raise HTTPException(status_code=403, detail="无权限")

    request = await makeup_request_service.approve(db, request_id, approved, current_user.id)
    if not request:
        raise HTTPException(status_code=404, detail="补卡申请不存在")
    return ResponseModel(data=request)