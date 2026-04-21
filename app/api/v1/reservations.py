"""
预定 API
"""
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from typing import List
from app.core.database import get_db
from app.schemas import (
    ReservationCreate, ReservationUpdate, ReservationResponse, ConflictCheck, ResponseModel
)
from app.services import reservation_service
from app.api.v1.auth import get_current_user
from app.schemas.user import UserResponse

router = APIRouter(prefix="/reservations", tags=["预定"])


@router.get("", response_model=ResponseModel[List[ReservationResponse]])
async def get_reservations(
    room_id: int = None,
    db: AsyncSession = Depends(get_db),
    current_user: UserResponse = Depends(get_current_user)
):
    """获取预定列表"""
    if room_id:
        reservations = await reservation_service.find_by_room(db, room_id)
    else:
        reservations = await reservation_service.find_by_user(db, current_user.id)
    return ResponseModel(data=reservations)


@router.get("/my", response_model=ResponseModel[List[ReservationResponse]])
async def get_my_reservations(
    db: AsyncSession = Depends(get_db),
    current_user: UserResponse = Depends(get_current_user)
):
    """获取我的预定"""
    reservations = await reservation_service.find_by_user(db, current_user.id)
    return ResponseModel(data=reservations)


@router.get("/{reservation_id}", response_model=ResponseModel[ReservationResponse])
async def get_reservation(
    reservation_id: int,
    db: AsyncSession = Depends(get_db),
    current_user: UserResponse = Depends(get_current_user)
):
    """获取预定详情"""
    reservation = await reservation_service.get_by_id(db, reservation_id)
    if not reservation:
        raise HTTPException(status_code=404, detail="预定不存在")
    return ResponseModel(data=reservation)


@router.post("", response_model=ResponseModel[ReservationResponse])
async def create_reservation(
    data: ReservationCreate,
    db: AsyncSession = Depends(get_db),
    current_user: UserResponse = Depends(get_current_user)
):
    """创建预定"""
    # 检查冲突
    conflict = await reservation_service.check_conflict(db, data.room_id, data.start_time, data.end_time)
    if conflict:
        raise HTTPException(status_code=400, detail=f"时间冲突，与预定 {conflict.id} 冲突")

    reservation = await reservation_service.create(db, {
        **data.model_dump(by_alias=False),
        "user_id": current_user.id
    })
    return ResponseModel(data=reservation)


@router.post("/check-conflict")
async def check_conflict(
    data: ConflictCheck,
    db: AsyncSession = Depends(get_db),
    current_user: UserResponse = Depends(get_current_user)
):
    """检查预定冲突"""
    conflict = await reservation_service.check_conflict(
        db, data.room_id, data.start_time, data.end_time, data.exclude_id
    )
    return ResponseModel(data={"hasConflict": conflict is not None, "conflict": conflict})


@router.put("/{reservation_id}", response_model=ResponseModel[ReservationResponse])
async def update_reservation(
    reservation_id: int,
    data: ReservationUpdate,
    db: AsyncSession = Depends(get_db),
    current_user: UserResponse = Depends(get_current_user)
):
    """更新预定"""
    reservation = await reservation_service.get_by_id(db, reservation_id)
    if not reservation:
        raise HTTPException(status_code=404, detail="预定不存在")
    if reservation.user_id != current_user.id:
        raise HTTPException(status_code=403, detail="无权限")

    # 检查冲突
    if data.start_time and data.end_time:
        conflict = await reservation_service.check_conflict(
            db, reservation.room_id, data.start_time, data.end_time, reservation_id
        )
        if conflict:
            raise HTTPException(status_code=400, detail="时间冲突")

    updated = await reservation_service.update(db, reservation_id, data.model_dump(exclude_unset=True, by_alias=False))
    return ResponseModel(data=updated)


@router.delete("/{reservation_id}")
async def cancel_reservation(
    reservation_id: int,
    db: AsyncSession = Depends(get_db),
    current_user: UserResponse = Depends(get_current_user)
):
    """取消预定"""
    reservation = await reservation_service.get_by_id(db, reservation_id)
    if not reservation:
        raise HTTPException(status_code=404, detail="预定不存在")
    if reservation.user_id != current_user.id:
        raise HTTPException(status_code=403, detail="无权限")

    await reservation_service.update(db, reservation_id, {"status": "cancelled"})
    return ResponseModel(message="取消成功")
