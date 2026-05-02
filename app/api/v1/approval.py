"""
审批模块 API
"""
from fastapi import APIRouter, Depends, Request
from app.core.exceptions import BizException
from app.core.error_codes import ErrorCode
from sqlalchemy.ext.asyncio import AsyncSession
from typing import List, Optional
from app.core.database import get_db
from app.schemas.approval import (
    ApprovalChainCreate, ApprovalChainUpdate, ApprovalChainResponse,
    ApprovalNodeCreate, ApprovalNodeResponse,
    ApprovalRequestCreate, ApprovalRequestResponse,
    ApprovalRecordResponse, ApprovalReminderResponse,
    ApprovalChainQuery, ApprovalRequestQuery
)
from app.schemas.common import ResponseModel
from app.services.approval_service import approval_service
from app.api.v1.auth import get_current_user
from app.schemas.user import UserResponse

router = APIRouter(prefix="/approval", tags=["审批"])


# ========== 审批链管理 ==========

@router.post("/chains", response_model=ResponseModel[ApprovalChainResponse])
async def create_chain(
    chain_data: ApprovalChainCreate,
    nodes: Optional[List[ApprovalNodeCreate]] = None,
    db: AsyncSession = Depends(get_db),
    current_user: UserResponse = Depends(get_current_user)
):
    """
    创建审批链

    - business_type: 业务类型（如 leave, trip, expense 等）
    - name: 审批链名称
    - description: 描述
    - is_enabled: 是否启用
    - nodes: 审批节点列表
    """
    try:
        chain = await approval_service.create_chain(
            db, chain_data, current_user.id, nodes
        )
        return ResponseModel(code=200, message="创建成功", data=chain)
    except ValueError as e:
        raise BizException(ErrorCode.APPROVAL_OPERATION_FAILED, str(e))


@router.get("/chains", response_model=ResponseModel[List[ApprovalChainResponse]])
async def list_chains(
    business_type: Optional[str] = None,
    name: Optional[str] = None,
    is_enabled: Optional[bool] = None,
    page: int = 1,
    page_size: int = 20,
    db: AsyncSession = Depends(get_db),
    current_user: UserResponse = Depends(get_current_user)
):
    """
    列出审批链

    支持按业务类型、名称、启用状态筛选
    """
    query = ApprovalChainQuery(
        business_type=business_type,
        name=name,
        is_enabled=is_enabled,
        page=page,
        page_size=page_size
    )
    chains, total = await approval_service.list_chains(db, query)
    return ResponseModel(
        code=200,
        message="success",
        data={
            "items": chains,
            "total": total,
            "page": page,
            "page_size": page_size
        }
    )


@router.get("/chains/{chain_id}", response_model=ResponseModel[ApprovalChainResponse])
async def get_chain(
    chain_id: int,
    db: AsyncSession = Depends(get_db),
    current_user: UserResponse = Depends(get_current_user)
):
    """获取审批链详情"""
    chain = await approval_service.get_chain(db, chain_id, include_nodes=True)
    if not chain:
        raise BizException(ErrorCode.APPROVAL_CHAIN_NOT_FOUND)
    return ResponseModel(code=200, message="success", data=chain)


@router.put("/chains/{chain_id}", response_model=ResponseModel[ApprovalChainResponse])
async def update_chain(
    chain_id: int,
    chain_data: ApprovalChainUpdate,
    db: AsyncSession = Depends(get_db),
    current_user: UserResponse = Depends(get_current_user)
):
    """更新审批链"""
    chain = await approval_service.update_chain(db, chain_id, chain_data)
    if not chain:
        raise BizException(ErrorCode.APPROVAL_CHAIN_NOT_FOUND)
    return ResponseModel(code=200, message="更新成功", data=chain)


@router.delete("/chains/{chain_id}")
async def delete_chain(
    chain_id: int,
    db: AsyncSession = Depends(get_db),
    current_user: UserResponse = Depends(get_current_user)
):
    """删除审批链"""
    try:
        success = await approval_service.delete_chain(db, chain_id)
        if not success:
            raise BizException(ErrorCode.APPROVAL_CHAIN_NOT_FOUND)
        return ResponseModel(code=200, message="删除成功", data=None)
    except ValueError as e:
        raise BizException(ErrorCode.APPROVAL_OPERATION_FAILED, str(e))


# ========== 审批申请 ==========

@router.post("/requests", response_model=ResponseModel[ApprovalRequestResponse])
async def submit_request(
    request_data: ApprovalRequestCreate,
    db: AsyncSession = Depends(get_db),
    current_user: UserResponse = Depends(get_current_user)
):
    """
    提交审批申请

    - business_type: 业务类型
    - title: 申请标题
    - content: 申请内容（JSON格式）
    - attachments: 附件列表
    - chain_id: 审批链ID（可选）
    """
    try:
        approval_request = await approval_service.submit_request(
            db, request_data, current_user.id
        )
        return ResponseModel(code=200, message="提交成功", data=approval_request)
    except ValueError as e:
        raise BizException(ErrorCode.APPROVAL_OPERATION_FAILED, str(e))


@router.get("/requests", response_model=ResponseModel)
async def list_requests(
    business_type: Optional[str] = None,
    request_no: Optional[str] = None,
    applicant_id: Optional[int] = None,
    status: Optional[str] = None,
    current_approver_id: Optional[int] = None,
    page: int = 1,
    page_size: int = 20,
    db: AsyncSession = Depends(get_db),
    current_user: UserResponse = Depends(get_current_user)
):
    """
    列出审批申请

    支持按业务类型、申请编号、申请人、状态、当前审批人筛选
    - 管理员可查看所有申请
    - 普通用户仅可查看自己的申请或待审批的申请
    """
    query = ApprovalRequestQuery(
        business_type=business_type,
        request_no=request_no,
        applicant_id=applicant_id,
        status=status,
        current_approver_id=current_approver_id,
        page=page,
        page_size=page_size
    )

    # 普通用户只能查看自己的申请或待审批的申请
    if current_user.role != "admin":
        query.applicant_id = current_user.id

    requests, total = await approval_service.list_requests(db, query, include_chain=True)
    return ResponseModel(
        code=200,
        message="success",
        data={
            "items": requests,
            "total": total,
            "page": page,
            "page_size": page_size
        }
    )


@router.get("/requests/my", response_model=ResponseModel)
async def get_my_requests(
    status: Optional[str] = None,
    page: int = 1,
    page_size: int = 20,
    db: AsyncSession = Depends(get_db),
    current_user: UserResponse = Depends(get_current_user)
):
    """获取当前用户的申请记录"""
    query = ApprovalRequestQuery(
        applicant_id=current_user.id,
        status=status,
        page=page,
        page_size=page_size
    )
    requests, total = await approval_service.query_user_requests(db, current_user.id, query)
    return ResponseModel(
        code=200,
        message="success",
        data={
            "items": requests,
            "total": total,
            "page": page,
            "page_size": page_size
        }
    )


@router.get("/requests/pending", response_model=ResponseModel)
async def get_pending_requests(
    business_type: Optional[str] = None,
    page: int = 1,
    page_size: int = 20,
    db: AsyncSession = Depends(get_db),
    current_user: UserResponse = Depends(get_current_user)
):
    """获取当前用户待审批的申请"""
    query = ApprovalRequestQuery(
        business_type=business_type,
        page=page,
        page_size=page_size
    )
    requests, total = await approval_service.query_pending_approvals(
        db, current_user.id, query
    )
    return ResponseModel(
        code=200,
        message="success",
        data={
            "items": requests,
            "total": total,
            "page": page,
            "page_size": page_size
        }
    )


@router.get("/requests/{request_id}", response_model=ResponseModel[ApprovalRequestResponse])
async def get_request(
    request_id: int,
    db: AsyncSession = Depends(get_db),
    current_user: UserResponse = Depends(get_current_user)
):
    """获取审批申请详情"""
    approval_request = await approval_service.get_request(
        db, request_id, include_chain=True, include_records=True
    )
    if not approval_request:
        raise BizException(ErrorCode.APPROVAL_NOT_FOUND)
    return ResponseModel(code=200, message="success", data=approval_request)


# ========== 审批操作 ==========

@router.post("/requests/{request_id}/approve", response_model=ResponseModel[ApprovalRequestResponse])
async def approve_request(
    request_id: int,
    request: Request,
    comment: Optional[str] = None,
    db: AsyncSession = Depends(get_db),
    current_user: UserResponse = Depends(get_current_user)
):
    """
    审批通过

    只有当前审批人可以审批通过
    """
    try:
        approver_name = getattr(current_user, "name", None) or current_user.username
        approval_request = await approval_service.approve(
            db, request_id, current_user.id, approver_name, comment
        )
        return ResponseModel(code=200, message="审批通过", data=approval_request)
    except ValueError as e:
        raise BizException(ErrorCode.APPROVAL_OPERATION_FAILED, str(e))


@router.post("/requests/{request_id}/reject", response_model=ResponseModel[ApprovalRequestResponse])
async def reject_request(
    request_id: int,
    request: Request,
    comment: Optional[str] = None,
    db: AsyncSession = Depends(get_db),
    current_user: UserResponse = Depends(get_current_user)
):
    """
    审批拒绝

    只有当前审批人可以审批拒绝
    """
    try:
        approver_name = getattr(current_user, "name", None) or current_user.username
        approval_request = await approval_service.reject(
            db, request_id, current_user.id, approver_name, comment
        )
        return ResponseModel(code=200, message="审批拒绝", data=approval_request)
    except ValueError as e:
        raise BizException(ErrorCode.APPROVAL_OPERATION_FAILED, str(e))


@router.post("/requests/batch-approve", response_model=ResponseModel)
async def batch_approve_requests(
    request_ids: List[int],
    comment: Optional[str] = None,
    db: AsyncSession = Depends(get_db),
    current_user: UserResponse = Depends(get_current_user)
):
    """
    批量审批通过

    批量审批通过指定的申请列表
    """
    approver_name = getattr(current_user, "name", None) or current_user.username
    result = await approval_service.batch_approve(
        db, request_ids, current_user.id, approver_name, comment
    )
    return ResponseModel(
        code=200,
        message=f"批量审批完成，成功{result['success_count']}个，失败{result['failed_count']}个",
        data=result
    )


@router.post("/requests/{request_id}/remind", response_model=ResponseModel[ApprovalReminderResponse])
async def remind_request(
    request_id: int,
    db: AsyncSession = Depends(get_db),
    current_user: UserResponse = Depends(get_current_user)
):
    """
    催办

    催促当前审批人尽快审批
    """
    try:
        reminder = await approval_service.create_reminder(db, request_id, current_user.id)
        return ResponseModel(code=200, message="催办成功", data=reminder)
    except ValueError as e:
        raise BizException(ErrorCode.APPROVAL_OPERATION_FAILED, str(e))


@router.get("/requests/{request_id}/records", response_model=ResponseModel[List[ApprovalRecordResponse]])
async def get_request_records(
    request_id: int,
    db: AsyncSession = Depends(get_db),
    current_user: UserResponse = Depends(get_current_user)
):
    """获取申请的审批记录"""
    records = await approval_service.get_records(db, request_id)
    return ResponseModel(code=200, message="success", data=records)
