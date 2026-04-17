"""
请假申请 API
"""
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from typing import List
from app.core.database import get_db
from app.schemas import (
    LeaveCreate, LeaveUpdate, LeaveApprove, LeaveResponse, ResponseModel
)
from app.services import leave_service
from app.api.v1.auth import get_current_user
from app.schemas.user import UserResponse

router = APIRouter(prefix="/leaves", tags=["请假申请"])


@router.get("", response_model=ResponseModel[List[LeaveResponse]])
async def get_leaves(
    status: str = None,
    db: AsyncSession = Depends(get_db),
    current_user: UserResponse = Depends(get_current_user)
):
    """获取请假申请列表"""
    if current_user.role == "admin" and status:
        leaves = await leave_service.find_by_status(db, status)
    else:
        leaves = await leave_service.find_by_user(db, current_user.id)
    return ResponseModel(data=leaves)


@router.get("/pending", response_model=ResponseModel[List[LeaveResponse]])
async def get_pending_leaves(
    db: AsyncSession = Depends(get_db),
    current_user: UserResponse = Depends(get_current_user)
):
    """获取待审批请假申请（管理员）"""
    if current_user.role != "admin":
        raise HTTPException(status_code=403, detail="无权限")
    leaves = await leave_service.find_pending(db)
    return ResponseModel(data=leaves)


@router.get("/{leave_id}", response_model=ResponseModel[LeaveResponse])
async def get_leave(
    leave_id: int,
    db: AsyncSession = Depends(get_db),
    current_user: UserResponse = Depends(get_current_user)
):
    """获取请假申请详情"""
    leave = await leave_service.get_by_id(db, leave_id)
    if not leave:
        raise HTTPException(status_code=404, detail="请假申请不存在")
    return ResponseModel(data=leave)


@router.post("", response_model=ResponseModel[LeaveResponse])
async def create_leave(
    data: LeaveCreate,
    db: AsyncSession = Depends(get_db),
    current_user: UserResponse = Depends(get_current_user)
):
    """创建请假申请"""
    # 检查日期重叠
    overlap = await leave_service.check_overlap(db, current_user.id, data.startDate, data.endDate)
    if overlap:
        raise HTTPException(status_code=400, detail=f"日期与已存在的请假申请重叠")

    leave = await leave_service.create(db, {**data.model_dump(), "userId": current_user.id})
    return ResponseModel(data=leave)


@router.put("/{leave_id}", response_model=ResponseModel[LeaveResponse])
async def update_leave(
    leave_id: int,
    data: LeaveUpdate,
    db: AsyncSession = Depends(get_db),
    current_user: UserResponse = Depends(get_current_user)
):
    """更新请假申请"""
    leave = await leave_service.get_by_id(db, leave_id)
    if not leave:
        raise HTTPException(status_code=404, detail="请假申请不存在")
    if leave.userId != current_user.id:
        raise HTTPException(status_code=403, detail="无权限")
    if leave.status != "pending":
        raise HTTPException(status_code=400, detail="只能修改待审批的申请")

    # 检查日期重叠
    start = data.startDate or leave.startDate
    end = data.endDate or leave.endDate
    overlap = await leave_service.check_overlap(db, current_user.id, start, end, leave_id)
    if overlap:
        raise HTTPException(status_code=400, detail="日期与已存在的请假申请重叠")

    updated = await leave_service.update(db, leave_id, data.model_dump(exclude_unset=True))
    return ResponseModel(data=updated)


@router.post("/{leave_id}/approve", response_model=ResponseModel[LeaveResponse])
async def approve_leave(
    leave_id: int,
    data: LeaveApprove,
    db: AsyncSession = Depends(get_db),
    current_user: UserResponse = Depends(get_current_user)
):
    """审批请假申请（管理员）"""
    if current_user.role != "admin":
        raise HTTPException(status_code=403, detail="无权限")

    leave = await leave_service.approve(db, leave_id, data.approved, data.comment, current_user.id)
    if not leave:
        raise HTTPException(status_code=404, detail="请假申请不存在")
    return ResponseModel(data=leave)


@router.delete("/{leave_id}")
async def delete_leave(
    leave_id: int,
    db: AsyncSession = Depends(get_db),
    current_user: UserResponse = Depends(get_current_user)
):
    """删除请假申请"""
    leave = await leave_service.get_by_id(db, leave_id)
    if not leave:
        raise HTTPException(status_code=404, detail="请假申请不存在")
    if leave.userId != current_user.id:
        raise HTTPException(status_code=403, detail="无权限")
    if leave.status == "approved":
        raise HTTPException(status_code=400, detail="已通过的申请不能删除")

    await leave_service.delete(db, leave_id)
    return ResponseModel(message="删除成功")