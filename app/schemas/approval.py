"""
审批模块相关 Schema
"""
from pydantic import BaseModel
from typing import Optional, List
from datetime import datetime
from app.schemas.common import CamelModel


# ============ ApprovalChain 审批链 ============

class ApprovalChainBase(CamelModel):
    """审批链基础"""
    business_type: str
    name: str
    description: Optional[str] = None
    is_enabled: bool = True


class ApprovalChainCreate(ApprovalChainBase):
    """创建审批链"""
    pass


class ApprovalChainUpdate(CamelModel):
    """更新审批链"""
    name: Optional[str] = None
    description: Optional[str] = None
    is_enabled: Optional[bool] = None


class ApprovalChainResponse(ApprovalChainBase):
    """审批链响应"""
    id: int
    created_by: int
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None


# ============ ApprovalNode 审批节点 ============

class ApprovalNodeBase(CamelModel):
    """审批节点基础"""
    chain_id: int
    node_order: int
    node_type: str  # role/user/department_head
    node_value: str
    approval_mode: str = "or"  # or/and


class ApprovalNodeCreate(ApprovalNodeBase):
    """创建审批节点"""
    pass


class ApprovalNodeUpdate(CamelModel):
    """更新审批节点"""
    node_order: Optional[int] = None
    node_type: Optional[str] = None
    node_value: Optional[str] = None
    approval_mode: Optional[str] = None


class ApprovalNodeResponse(ApprovalNodeBase):
    """审批节点响应"""
    id: int
    created_at: Optional[datetime] = None


# ============ ApprovalRequest 审批申请 ============

class ApprovalRequestBase(CamelModel):
    """审批申请基础"""
    business_type: str
    title: str
    content: Optional[dict] = None
    attachments: Optional[List[dict]] = None


class ApprovalRequestCreate(ApprovalRequestBase):
    """创建审批申请"""
    chain_id: Optional[int] = None


class ApprovalRequestUpdate(CamelModel):
    """更新审批申请"""
    title: Optional[str] = None
    content: Optional[dict] = None
    attachments: Optional[List[dict]] = None


class ApprovalRequestResponse(ApprovalRequestBase):
    """审批申请响应"""
    id: int
    request_no: str
    chain_id: Optional[int] = None
    applicant_id: int
    current_node_id: Optional[int] = None
    current_approver_id: Optional[int] = None
    status: str = "pending"
    submitted_at: Optional[datetime] = None
    completed_at: Optional[datetime] = None
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None


# ============ ApprovalRecord 审批记录 ============

class ApprovalRecordBase(CamelModel):
    """审批记录基础"""
    request_id: int
    node_id: int
    approver_id: int
    approver_name: Optional[str] = None
    action: str  # approve/reject
    comment: Optional[str] = None


class ApprovalRecordCreate(ApprovalRecordBase):
    """创建审批记录"""
    pass


class ApprovalRecordResponse(ApprovalRecordBase):
    """审批记录响应"""
    id: int
    created_at: Optional[datetime] = None


# ============ ApprovalReminder 催办记录 ============

class ApprovalReminderBase(CamelModel):
    """催办记录基础"""
    request_id: int
    requester_id: int


class ApprovalReminderCreate(ApprovalReminderBase):
    """创建催办记录"""
    pass


class ApprovalReminderResponse(ApprovalReminderBase):
    """催办记录响应"""
    id: int
    reminder_count: int = 1
    last_reminded_at: Optional[datetime] = None
    created_at: Optional[datetime] = None


# ============ 分页和查询 Schema ============

class ApprovalChainQuery(CamelModel):
    """审批链查询参数"""
    business_type: Optional[str] = None
    name: Optional[str] = None
    is_enabled: Optional[bool] = None
    page: int = 1
    page_size: int = 20


class ApprovalRequestQuery(CamelModel):
    """审批申请查询参数"""
    business_type: Optional[str] = None
    request_no: Optional[str] = None
    applicant_id: Optional[int] = None
    status: Optional[str] = None
    current_approver_id: Optional[int] = None
    page: int = 1
    page_size: int = 20


class ApprovalRecordQuery(CamelModel):
    """审批记录查询参数"""
    request_id: Optional[int] = None
    node_id: Optional[int] = None
    approver_id: Optional[int] = None
    action: Optional[str] = None
    page: int = 1
    page_size: int = 20
