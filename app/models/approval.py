"""
审批模块数据模型
"""
from datetime import datetime
from sqlalchemy import Column, Integer, String, Boolean, Text, DateTime, ForeignKey, JSON
from sqlalchemy.sql import func
from sqlalchemy.orm import relationship
from app.core.database import Base


class ApprovalChain(Base):
    """审批链配置表"""
    __tablename__ = "approval_chains"

    id = Column(Integer, primary_key=True, index=True)
    business_type = Column(String(50), unique=True, nullable=False, index=True)
    name = Column(String(100), nullable=False)
    description = Column(Text)
    is_enabled = Column(Boolean, default=True, index=True)
    created_by = Column(Integer, nullable=False)
    created_at = Column(DateTime, server_default=func.now())
    updated_at = Column(DateTime, server_default=func.now(), onupdate=func.now())

    # 关联
    nodes = relationship("ApprovalNode", back_populates="chain", cascade="all, delete-orphan")
    requests = relationship("ApprovalRequest", back_populates="chain")


class ApprovalNode(Base):
    """审批节点表"""
    __tablename__ = "approval_nodes"

    id = Column(Integer, primary_key=True, index=True)
    chain_id = Column(Integer, ForeignKey("approval_chains.id", ondelete="CASCADE"), nullable=False, index=True)
    node_order = Column(Integer, nullable=False)
    node_type = Column(String(20), nullable=False)  # role/user/department_head
    node_value = Column(Text, nullable=False)
    approval_mode = Column(String(10), nullable=False)  # or/and
    created_at = Column(DateTime, server_default=func.now())

    # 关联
    chain = relationship("ApprovalChain", back_populates="nodes")


class ApprovalRequest(Base):
    """审批申请记录表"""
    __tablename__ = "approval_requests"

    id = Column(Integer, primary_key=True, index=True)
    request_no = Column(String(50), unique=True, nullable=False, index=True)
    business_type = Column(String(50), nullable=False, index=True)
    chain_id = Column(Integer, ForeignKey("approval_chains.id"))
    applicant_id = Column(Integer, nullable=False, index=True)
    title = Column(String(200), nullable=False)
    content = Column(JSON)
    attachments = Column(JSON)
    current_node_id = Column(Integer, ForeignKey("approval_nodes.id"))
    current_approver_id = Column(Integer, index=True)
    status = Column(String(20), default="pending", index=True)  # pending/approved/rejected
    submitted_at = Column(DateTime, server_default=func.now())
    completed_at = Column(DateTime)
    created_at = Column(DateTime, server_default=func.now())
    updated_at = Column(DateTime, server_default=func.now(), onupdate=func.now())

    # 关联
    chain = relationship("ApprovalChain", back_populates="requests")
    current_node = relationship("ApprovalNode")
    records = relationship("ApprovalRecord", back_populates="request", cascade="all, delete-orphan")
    reminders = relationship("ApprovalReminder", back_populates="request", cascade="all, delete-orphan")


class ApprovalRecord(Base):
    """审批记录表"""
    __tablename__ = "approval_records"

    id = Column(Integer, primary_key=True, index=True)
    request_id = Column(Integer, ForeignKey("approval_requests.id", ondelete="CASCADE"), nullable=False, index=True)
    node_id = Column(Integer, ForeignKey("approval_nodes.id"), nullable=False)
    approver_id = Column(Integer, nullable=False, index=True)
    approver_name = Column(String(100))
    action = Column(String(20), nullable=False)  # approve/reject
    comment = Column(Text)
    created_at = Column(DateTime, server_default=func.now())

    # 关联
    request = relationship("ApprovalRequest", back_populates="records")
    node = relationship("ApprovalNode")


class ApprovalReminder(Base):
    """催办记录表"""
    __tablename__ = "approval_reminders"

    id = Column(Integer, primary_key=True, index=True)
    request_id = Column(Integer, ForeignKey("approval_requests.id", ondelete="CASCADE"), nullable=False, index=True)
    requester_id = Column(Integer, nullable=False, index=True)
    reminder_count = Column(Integer, default=1)
    last_reminded_at = Column(DateTime, server_default=func.now())
    created_at = Column(DateTime, server_default=func.now())

    # 关联
    request = relationship("ApprovalRequest", back_populates="reminders")
