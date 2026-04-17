"""
差旅申请 API
"""
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from typing import List
from app.core.database import get_db
from app.schemas import (
    TripCreate, TripUpdate, TripApprove, TripResponse, ResponseModel
)
from app.services import trip_service
from app.api.v1.auth import get_current_user
from app.schemas.user import UserResponse

router = APIRouter(prefix="/trips", tags=["差旅申请"])


@router.get("", response_model=ResponseModel[List[TripResponse]])
async def get_trips(
    status: str = None,
    db: AsyncSession = Depends(get_db),
    current_user: UserResponse = Depends(get_current_user)
):
    """获取差旅申请列表"""
    if current_user.role == "admin" and status:
        trips = await trip_service.find_by_status(db, status)
    else:
        trips = await trip_service.find_by_user(db, current_user.id)
    return ResponseModel(data=trips)


@router.get("/pending", response_model=ResponseModel[List[TripResponse]])
async def get_pending_trips(
    db: AsyncSession = Depends(get_db),
    current_user: UserResponse = Depends(get_current_user)
):
    """获取待审批差旅申请（管理员）"""
    if current_user.role != "admin":
        raise HTTPException(status_code=403, detail="无权限")
    trips = await trip_service.find_pending(db)
    return ResponseModel(data=trips)


@router.get("/{trip_id}", response_model=ResponseModel[TripResponse])
async def get_trip(
    trip_id: int,
    db: AsyncSession = Depends(get_db),
    current_user: UserResponse = Depends(get_current_user)
):
    """获取差旅申请详情"""
    trip = await trip_service.get_by_id(db, trip_id)
    if not trip:
        raise HTTPException(status_code=404, detail="差旅申请不存在")
    return ResponseModel(data=trip)


@router.post("", response_model=ResponseModel[TripResponse])
async def create_trip(
    data: TripCreate,
    db: AsyncSession = Depends(get_db),
    current_user: UserResponse = Depends(get_current_user)
):
    """创建差旅申请"""
    trip = await trip_service.create(db, {**data.model_dump(), "userId": current_user.id})
    return ResponseModel(data=trip)


@router.put("/{trip_id}", response_model=ResponseModel[TripResponse])
async def update_trip(
    trip_id: int,
    data: TripUpdate,
    db: AsyncSession = Depends(get_db),
    current_user: UserResponse = Depends(get_current_user)
):
    """更新差旅申请"""
    trip = await trip_service.get_by_id(db, trip_id)
    if not trip:
        raise HTTPException(status_code=404, detail="差旅申请不存在")
    if trip.userId != current_user.id:
        raise HTTPException(status_code=403, detail="无权限")
    if trip.status != "pending":
        raise HTTPException(status_code=400, detail="只能修改待审批的申请")

    updated = await trip_service.update(db, trip_id, data.model_dump(exclude_unset=True))
    return ResponseModel(data=updated)


@router.post("/{trip_id}/approve", response_model=ResponseModel[TripResponse])
async def approve_trip(
    trip_id: int,
    data: TripApprove,
    db: AsyncSession = Depends(get_db),
    current_user: UserResponse = Depends(get_current_user)
):
    """审批差旅申请（管理员）"""
    if current_user.role != "admin":
        raise HTTPException(status_code=403, detail="无权限")

    trip = await trip_service.approve(db, trip_id, data.approved, data.comment, current_user.id)
    if not trip:
        raise HTTPException(status_code=404, detail="差旅申请不存在")
    return ResponseModel(data=trip)


@router.delete("/{trip_id}")
async def delete_trip(
    trip_id: int,
    db: AsyncSession = Depends(get_db),
    current_user: UserResponse = Depends(get_current_user)
):
    """删除差旅申请"""
    trip = await trip_service.get_by_id(db, trip_id)
    if not trip:
        raise HTTPException(status_code=404, detail="差旅申请不存在")
    if trip.userId != current_user.id:
        raise HTTPException(status_code=403, detail="无权限")
    if trip.status == "approved":
        raise HTTPException(status_code=400, detail="已通过的申请不能删除")

    await trip_service.delete(db, trip_id)
    return ResponseModel(message="删除成功")