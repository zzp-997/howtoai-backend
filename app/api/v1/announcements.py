"""
公告通知 API
"""
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from typing import List
from app.core.database import get_db
from app.schemas import AnnouncementCreate, AnnouncementUpdate, AnnouncementResponse, ResponseModel
from app.services import announcement_service
from app.api.v1.auth import get_current_user
from app.schemas.user import UserResponse

router = APIRouter(prefix="/announcements", tags=["公告通知"])


@router.get("", response_model=ResponseModel[List[AnnouncementResponse]])
async def get_announcements(
    category: str = None,
    db: AsyncSession = Depends(get_db),
    current_user: UserResponse = Depends(get_current_user)
):
    """获取公告列表"""
    if category:
        announcements = await announcement_service.find_by_category(db, category)
    else:
        announcements = await announcement_service.find_all_ordered(db)
    return ResponseModel(data=announcements)


@router.get("/unread", response_model=ResponseModel[List[AnnouncementResponse]])
async def get_unread_announcements(
    db: AsyncSession = Depends(get_db),
    current_user: UserResponse = Depends(get_current_user)
):
    """获取未读公告"""
    announcements = await announcement_service.find_unread(db, current_user.id)
    return ResponseModel(data=announcements)


@router.get("/unread-count")
async def get_unread_count(
    db: AsyncSession = Depends(get_db),
    current_user: UserResponse = Depends(get_current_user)
):
    """获取未读公告数量"""
    count = await announcement_service.get_unread_count(db, current_user.id)
    return ResponseModel(data={"count": count})


@router.get("/{announcement_id}", response_model=ResponseModel[AnnouncementResponse])
async def get_announcement(
    announcement_id: int,
    db: AsyncSession = Depends(get_db),
    current_user: UserResponse = Depends(get_current_user)
):
    """获取公告详情"""
    announcement = await announcement_service.get_by_id(db, announcement_id)
    if not announcement:
        raise HTTPException(status_code=404, detail="公告不存在")

    # 标记已读
    await announcement_service.mark_as_read(db, announcement_id, current_user.id)
    return ResponseModel(data=announcement)


@router.post("/{announcement_id}/read")
async def mark_as_read(
    announcement_id: int,
    db: AsyncSession = Depends(get_db),
    current_user: UserResponse = Depends(get_current_user)
):
    """标记公告已读"""
    await announcement_service.mark_as_read(db, announcement_id, current_user.id)
    return ResponseModel(message="已标记已读")


@router.post("", response_model=ResponseModel[AnnouncementResponse])
async def create_announcement(
    data: AnnouncementCreate,
    db: AsyncSession = Depends(get_db),
    current_user: UserResponse = Depends(get_current_user)
):
    """创建公告（管理员）"""
    if current_user.role != "admin":
        raise HTTPException(status_code=403, detail="无权限")

    from datetime import datetime
    announcement = await announcement_service.create(db, {
        **data.model_dump(),
        "publishTime": datetime.now()
    })
    return ResponseModel(data=announcement)


@router.put("/{announcement_id}", response_model=ResponseModel[AnnouncementResponse])
async def update_announcement(
    announcement_id: int,
    data: AnnouncementUpdate,
    db: AsyncSession = Depends(get_db),
    current_user: UserResponse = Depends(get_current_user)
):
    """更新公告（管理员）"""
    if current_user.role != "admin":
        raise HTTPException(status_code=403, detail="无权限")

    announcement = await announcement_service.update(db, announcement_id, data.model_dump(exclude_unset=True))
    if not announcement:
        raise HTTPException(status_code=404, detail="公告不存在")
    return ResponseModel(data=announcement)


@router.delete("/{announcement_id}")
async def delete_announcement(
    announcement_id: int,
    db: AsyncSession = Depends(get_db),
    current_user: UserResponse = Depends(get_current_user)
):
    """删除公告（管理员）"""
    if current_user.role != "admin":
        raise HTTPException(status_code=403, detail="无权限")

    success = await announcement_service.delete(db, announcement_id)
    if not success:
        raise HTTPException(status_code=404, detail="公告不存在")
    return ResponseModel(message="删除成功")