"""
意见反馈 API
"""
from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from sqlalchemy.ext.asyncio import AsyncSession
from app.core.database import get_db
from app.schemas.feedback import (
    FeedbackCreate, FeedbackReplySchema, FeedbackQuerySchema, FeedbackResponse
)
from app.schemas.common import ResponseModel
from app.services.feedback_service import feedback_service
from app.services.auth_service import auth_service
from app.core.security_module.token_service import TokenService
from app.schemas.user import UserResponse
from typing import Optional
import logging

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/feedbacks", tags=["意见反馈"])
security = HTTPBearer()


async def get_current_user(
    credentials: HTTPAuthorizationCredentials = Depends(security),
    db: AsyncSession = Depends(get_db)
) -> UserResponse:
    """获取当前用户"""
    token = credentials.credentials

    # 验证Token
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


async def get_current_admin_user(
    credentials: HTTPAuthorizationCredentials = Depends(security),
    db: AsyncSession = Depends(get_db)
) -> UserResponse:
    """获取当前管理员用户"""
    user = await get_current_user(credentials, db)

    if user.role != "admin":
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="需要管理员权限"
        )

    return user


@router.post("", response_model=ResponseModel)
async def submit_feedback(
    feedback_data: FeedbackCreate,
    current_user: UserResponse = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """
    用户提交反馈

    用户可以提交意见反馈，包括建议、bug、优化或其他类型
    """
    result = await feedback_service.submit(
        db=db,
        user_id=current_user.id,
        user_name=current_user.username,
        feedback_data=feedback_data
    )

    if not result.get("success"):
        return ResponseModel(
            code=400,
            message=result.get("message"),
            data=None
        )

    return ResponseModel(
        code=200,
        message=result.get("message"),
        data=result.get("data")
    )


@router.get("", response_model=ResponseModel)
async def query_feedbacks(
    type: Optional[str] = None,
    status: Optional[str] = None,
    user_id: Optional[int] = None,
    keyword: Optional[str] = None,
    start_date: Optional[str] = None,
    end_date: Optional[str] = None,
    page: int = 1,
    page_size: int = 20,
    current_user: UserResponse = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """
    查询反馈列表

    - 普通用户：只能查看自己的反馈
    - 管理员：可以查看所有反馈，支持按用户ID筛选
    """
    is_admin = current_user.role == "admin"

    # 构建查询参数
    query_params = FeedbackQuerySchema(
        type=type,
        status=status,
        user_id=user_id if is_admin else current_user.id,
        keyword=keyword,
        start_date=start_date,
        end_date=end_date
    )

    result = await feedback_service.query(
        db=db,
        query_params=query_params,
        is_admin=is_admin
    )

    if not result.get("success"):
        return ResponseModel(
            code=400,
            message=result.get("message"),
            data=None
        )

    # 分页处理
    total = result.get("total", 0)
    feedbacks = result.get("data", [])
    start_idx = (page - 1) * page_size
    end_idx = start_idx + page_size
    paginated_data = feedbacks[start_idx:end_idx]

    return ResponseModel(
        code=200,
        message="success",
        data={
            "list": paginated_data,
            "total": total,
            "page": page,
            "page_size": page_size
        }
    )


@router.get("/{feedback_id}", response_model=ResponseModel)
async def get_feedback_detail(
    feedback_id: int,
    current_user: UserResponse = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """
    获取反馈详情

    - 普通用户：只能查看自己的反馈
    - 管理员：可以查看所有反馈
    """
    feedback = await feedback_service.get_by_id(db, feedback_id)

    if not feedback:
        return ResponseModel(code=404, message="反馈不存在", data=None)

    # 权限检查
    if current_user.role != "admin" and feedback.user_id != current_user.id:
        return ResponseModel(code=403, message="无权查看此反馈", data=None)

    return ResponseModel(
        code=200,
        message="success",
        data={
            "id": feedback.id,
            "feedback_no": feedback.feedback_no,
            "user_id": feedback.user_id,
            "user_name": feedback.user_name,
            "type": feedback.type,
            "title": feedback.title,
            "content": feedback.content,
            "images": feedback.images,
            "status": feedback.status,
            "handler_id": feedback.handler_id,
            "handler_name": feedback.handler_name,
            "reply_content": feedback.reply_content,
            "replied_at": feedback.replied_at,
            "closed_at": feedback.closed_at,
            "created_at": feedback.created_at,
            "updated_at": feedback.updated_at
        }
    )


@router.put("/{feedback_id}/reply", response_model=ResponseModel)
async def reply_feedback(
    feedback_id: int,
    reply_data: FeedbackReplySchema,
    current_admin: UserResponse = Depends(get_current_admin_user),
    db: AsyncSession = Depends(get_db)
):
    """
    管理员回复反馈

    管理员可以对反馈进行回复
    """
    result = await feedback_service.reply(
        db=db,
        feedback_id=feedback_id,
        handler_id=current_admin.id,
        handler_name=current_admin.username,
        reply_data=reply_data
    )

    if not result.get("success"):
        return ResponseModel(
            code=400,
            message=result.get("message"),
            data=None
        )

    return ResponseModel(
        code=200,
        message=result.get("message"),
        data=result.get("data")
    )


@router.put("/{feedback_id}/close", response_model=ResponseModel)
async def close_feedback(
    feedback_id: int,
    current_admin: UserResponse = Depends(get_current_admin_user),
    db: AsyncSession = Depends(get_db)
):
    """
    关闭反馈

    管理员可以关闭某个反馈
    """
    result = await feedback_service.close(
        db=db,
        feedback_id=feedback_id,
        handler_id=current_admin.id,
        handler_name=current_admin.username
    )

    if not result.get("success"):
        return ResponseModel(
            code=400,
            message=result.get("message"),
            data=None
        )

    return ResponseModel(
        code=200,
        message=result.get("message"),
        data=result.get("data")
    )
