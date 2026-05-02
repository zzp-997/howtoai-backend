"""
消息中心 API - 消息相关接口
"""
from fastapi import APIRouter, Depends, HTTPException, status, Query
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from sqlalchemy.ext.asyncio import AsyncSession
from app.core.database import get_db
from app.schemas.user import UserResponse
from app.schemas.message import MessageQuery, MessageResponse
from app.schemas.common import ResponseModel
from app.services.message_service import message_service
from typing import Optional

router = APIRouter(prefix="/messages", tags=["消息中心"])
security = HTTPBearer()


async def get_current_user(
    credentials: HTTPAuthorizationCredentials = Depends(security),
    db: AsyncSession = Depends(get_db)
) -> UserResponse:
    """获取当前用户"""
    from app.core.security_module.token_service import TokenService
    from app.services.auth_service import auth_service

    token = credentials.credentials
    payload = TokenService.verify_token(token, "access")
    if not payload:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="无效的认证令牌"
        )

    user_id = payload.get("sub")
    user = await auth_service.get_by_id(db, int(user_id))
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="用户不存在"
        )

    return UserResponse.model_validate(user)


@router.get("")
async def get_messages(
    type: Optional[str] = Query(None, description="消息类型（approval/system/task）"),
    is_read: Optional[bool] = Query(None, description="是否已读"),
    page: int = Query(1, ge=1, description="页码"),
    page_size: int = Query(20, ge=1, le=100, description="每页数量"),
    current_user: UserResponse = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """
    获取消息列表（分页）

    - type: 消息类型（approval/system/task）
    - is_read: 是否已读
    - page: 页码
    - page_size: 每页数量
    """
    query = MessageQuery(
        user_id=current_user.id,
        type=type,
        is_read=is_read,
        page=page,
        page_size=page_size
    )
    result = await message_service.get_messages(db, current_user.id, query)

    return ResponseModel(
        code=200,
        message="success",
        data=result
    )


@router.get("/unread-count")
async def get_unread_count(
    msg_type: Optional[str] = None,
    current_user: UserResponse = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """
    获取未读消息数量

    - msg_type: 消息类型（可选，用于筛选特定类型）
    """
    count = await message_service.get_unread_count(db, current_user.id, msg_type)

    return ResponseModel(
        code=200,
        message="success",
        data={"unread_count": count}
    )


@router.put("/{message_id}/read")
async def mark_message_as_read(
    message_id: int,
    current_user: UserResponse = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """
    标记消息为已读

    - message_id: 消息ID
    """
    message = await message_service.mark_as_read(db, message_id, current_user.id)

    if not message:
        return ResponseModel(
            code=404,
            message="消息不存在或无权操作",
            data=None
        )

    return ResponseModel(
        code=200,
        message="标记已读成功",
        data=MessageResponse.model_validate(message)
    )


@router.put("/read-all")
async def mark_all_messages_as_read(
    msg_type: Optional[str] = None,
    current_user: UserResponse = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """
    标记所有消息为已读

    - msg_type: 消息类型（可选，用于筛选特定类型）
    """
    count = await message_service.mark_all_as_read(db, current_user.id, msg_type)

    return ResponseModel(
        code=200,
        message=f"已标记 {count} 条消息为已读",
        data={"updated_count": count}
    )
