"""
会议室 API
"""
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from typing import List
from app.core.database import get_db
from app.schemas import (
    MeetingRoomCreate, MeetingRoomUpdate, MeetingRoomResponse, ResponseModel
)
from app.services import meeting_room_service
from app.api.v1.auth import get_current_user
from app.schemas.user import UserResponse

router = APIRouter(prefix="/meeting-rooms", tags=["会议室"])


@router.get("", response_model=ResponseModel[List[MeetingRoomResponse]])
async def get_meeting_rooms(
    keyword: str = None,
    min_capacity: int = None,
    db: AsyncSession = Depends(get_db),
    current_user: UserResponse = Depends(get_current_user)
):
    """获取会议室列表"""
    if keyword:
        rooms = await meeting_room_service.search_by_name(db, keyword)
    elif min_capacity:
        rooms = await meeting_room_service.find_by_capacity(db, min_capacity)
    else:
        rooms = await meeting_room_service.get_active_rooms(db)
    return ResponseModel(data=rooms)


@router.get("/{room_id}", response_model=ResponseModel[MeetingRoomResponse])
async def get_meeting_room(
    room_id: int,
    db: AsyncSession = Depends(get_db),
    current_user: UserResponse = Depends(get_current_user)
):
    """获取会议室详情"""
    room = await meeting_room_service.get_by_id(db, room_id)
    if not room:
        raise HTTPException(status_code=404, detail="会议室不存在")
    return ResponseModel(data=room)


@router.post("", response_model=ResponseModel[MeetingRoomResponse])
async def create_meeting_room(
    data: MeetingRoomCreate,
    db: AsyncSession = Depends(get_db),
    current_user: UserResponse = Depends(get_current_user)
):
    """创建会议室（管理员）"""
    if current_user.role != "admin":
        raise HTTPException(status_code=403, detail="无权限")
    room = await meeting_room_service.create(db, data.model_dump(by_alias=False))
    return ResponseModel(data=room)


@router.put("/{room_id}", response_model=ResponseModel[MeetingRoomResponse])
async def update_meeting_room(
    room_id: int,
    data: MeetingRoomUpdate,
    db: AsyncSession = Depends(get_db),
    current_user: UserResponse = Depends(get_current_user)
):
    """更新会议室（管理员）"""
    if current_user.role != "admin":
        raise HTTPException(status_code=403, detail="无权限")
    room = await meeting_room_service.update(db, room_id, data.model_dump(exclude_unset=True, by_alias=False))
    if not room:
        raise HTTPException(status_code=404, detail="会议室不存在")
    return ResponseModel(data=room)


@router.delete("/{room_id}")
async def delete_meeting_room(
    room_id: int,
    db: AsyncSession = Depends(get_db),
    current_user: UserResponse = Depends(get_current_user)
):
    """删除会议室（管理员）"""
    if current_user.role != "admin":
        raise HTTPException(status_code=403, detail="无权限")
    success = await meeting_room_service.delete(db, room_id)
    if not success:
        raise HTTPException(status_code=404, detail="会议室不存在")
    return ResponseModel(message="删除成功")
