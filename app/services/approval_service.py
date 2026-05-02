"""
审批服务 - 审批链管理和审批流程处理
"""
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func, and_, or_
from sqlalchemy.orm import selectinload
from typing import Optional, List, Dict, Any
from datetime import datetime
import uuid
import logging

from app.models.approval import (
    ApprovalChain, ApprovalNode, ApprovalRequest,
    ApprovalRecord, ApprovalReminder
)
from app.schemas.approval import (
    ApprovalChainCreate, ApprovalChainUpdate,
    ApprovalNodeCreate, ApprovalNodeUpdate,
    ApprovalRequestCreate, ApprovalRequestUpdate,
    ApprovalRecordCreate,
    ApprovalChainQuery, ApprovalRequestQuery, ApprovalRecordQuery
)

logger = logging.getLogger(__name__)


class ApprovalService:
    """审批服务类"""

    # ========== 审批链管理 ==========

    async def create_chain(self, db: AsyncSession, chain_data: ApprovalChainCreate,
                           creator_id: int, nodes: List[ApprovalNodeCreate] = None) -> ApprovalChain:
        """
        创建审批链

        Args:
            db: 数据库会话
            chain_data: 审批链数据
            creator_id: 创建人ID
            nodes: 审批节点列表

        Returns:
            创建的审批链
        """
        # 检查业务类型是否已存在
        existing = await db.execute(
            select(ApprovalChain).where(ApprovalChain.business_type == chain_data.business_type)
        )
        if existing.scalar_one_or_none():
            raise ValueError(f"业务类型 {chain_data.business_type} 的审批链已存在")

        # 创建审批链
        chain = ApprovalChain(
            business_type=chain_data.business_type,
            name=chain_data.name,
            description=chain_data.description,
            is_enabled=chain_data.is_enabled,
            created_by=creator_id
        )
        db.add(chain)
        await db.flush()

        # 添加审批节点
        if nodes:
            for node_data in nodes:
                node = ApprovalNode(
                    chain_id=chain.id,
                    node_order=node_data.node_order,
                    node_type=node_data.node_type,
                    node_value=node_data.node_value,
                    approval_mode=node_data.approval_mode
                )
                db.add(node)

        await db.commit()
        await db.refresh(chain)
        return chain

    async def update_chain(self, db: AsyncSession, chain_id: int,
                           chain_data: ApprovalChainUpdate) -> Optional[ApprovalChain]:
        """
        更新审批链

        Args:
            db: 数据库会话
            chain_id: 审批链ID
            chain_data: 更新数据

        Returns:
            更新后的审批链
        """
        chain = await self.get_chain(db, chain_id)
        if not chain:
            return None

        update_data = chain_data.model_dump(exclude_unset=True)
        for key, value in update_data.items():
            if value is not None:
                setattr(chain, key, value)

        await db.commit()
        await db.refresh(chain)
        return chain

    async def delete_chain(self, db: AsyncSession, chain_id: int) -> bool:
        """
        删除审批链

        Args:
            db: 数据库会话
            chain_id: 审批链ID

        Returns:
            是否删除成功
        """
        chain = await self.get_chain(db, chain_id)
        if not chain:
            return False

        # 检查是否有正在使用的申请
        result = await db.execute(
            select(ApprovalRequest).where(
                and_(
                    ApprovalRequest.chain_id == chain_id,
                    ApprovalRequest.status.in_(["pending", "approved"])
                )
            ).limit(1)
        )
        if result.scalar_one_or_none():
            raise ValueError("该审批链存在正在处理的申请，无法删除")

        await db.delete(chain)
        await db.commit()
        return True

    async def get_chain(self, db: AsyncSession, chain_id: int,
                        include_nodes: bool = False) -> Optional[ApprovalChain]:
        """
        获取审批链

        Args:
            db: 数据库会话
            chain_id: 审批链ID
            include_nodes: 是否包含节点信息

        Returns:
            审批链
        """
        query = select(ApprovalChain).where(ApprovalChain.id == chain_id)
        if include_nodes:
            query = query.options(selectinload(ApprovalChain.nodes))

        result = await db.execute(query)
        return result.scalar_one_or_none()

    async def list_chains(self, db: AsyncSession, query: ApprovalChainQuery,
                          include_nodes: bool = False) -> tuple[List[ApprovalChain], int]:
        """
        列出审批链

        Args:
            db: 数据库会话
            query: 查询参数
            include_nodes: 是否包含节点信息

        Returns:
            (审批链列表, 总数)
        """
        stmt = select(ApprovalChain)

        # 条件过滤
        if query.business_type:
            stmt = stmt.where(ApprovalChain.business_type == query.business_type)
        if query.name:
            stmt = stmt.where(ApprovalChain.name.like(f"%{query.name}%"))
        if query.is_enabled is not None:
            stmt = stmt.where(ApprovalChain.is_enabled == query.is_enabled)

        # 统计总数
        count_stmt = select(func.count()).select_from(stmt.subquery())
        total_result = await db.execute(count_stmt)
        total = total_result.scalar() or 0

        # 分页
        offset = (query.page - 1) * query.page_size
        stmt = stmt.order_by(ApprovalChain.id.desc()).offset(offset).limit(query.page_size)

        if include_nodes:
            stmt = stmt.options(selectinload(ApprovalChain.nodes))

        result = await db.execute(stmt)
        chains = result.scalars().all()

        return list(chains), total

    # ========== 审批节点管理 ==========

    async def add_node(self, db: AsyncSession, chain_id: int,
                       node_data: ApprovalNodeCreate) -> ApprovalNode:
        """
        添加审批节点

        Args:
            db: 数据库会话
            chain_id: 审批链ID
            node_data: 节点数据

        Returns:
            创建的节点
        """
        chain = await self.get_chain(db, chain_id)
        if not chain:
            raise ValueError("审批链不存在")

        node = ApprovalNode(
            chain_id=chain_id,
            node_order=node_data.node_order,
            node_type=node_data.node_type,
            node_value=node_data.node_value,
            approval_mode=node_data.approval_mode
        )
        db.add(node)
        await db.commit()
        await db.refresh(node)
        return node

    async def update_node(self, db: AsyncSession, node_id: int,
                          node_data: ApprovalNodeUpdate) -> Optional[ApprovalNode]:
        """
        更新审批节点

        Args:
            db: 数据库会话
            node_id: 节点ID
            node_data: 更新数据

        Returns:
            更新后的节点
        """
        result = await db.execute(select(ApprovalNode).where(ApprovalNode.id == node_id))
        node = result.scalar_one_or_none()
        if not node:
            return None

        update_data = node_data.model_dump(exclude_unset=True)
        for key, value in update_data.items():
            if value is not None:
                setattr(node, key, value)

        await db.commit()
        await db.refresh(node)
        return node

    async def delete_node(self, db: AsyncSession, node_id: int) -> bool:
        """
        删除审批节点

        Args:
            db: 数据库会话
            node_id: 节点ID

        Returns:
            是否删除成功
        """
        result = await db.execute(select(ApprovalNode).where(ApprovalNode.id == node_id))
        node = result.scalar_one_or_none()
        if not node:
            return False

        # 检查是否有申请正在使用此节点
        check_result = await db.execute(
            select(ApprovalRequest).where(
                ApprovalRequest.current_node_id == node_id
            ).limit(1)
        )
        if check_result.scalar_one_or_none():
            raise ValueError("该节点存在正在处理的申请，无法删除")

        await db.delete(node)
        await db.commit()
        return True

    # ========== 审批流程 ==========

    async def submit_request(self, db: AsyncSession, request_data: ApprovalRequestCreate,
                             applicant_id: int) -> ApprovalRequest:
        """
        提交审批申请

        Args:
            db: 数据库会话
            request_data: 申请数据
            applicant_id: 申请人ID

        Returns:
            创建的申请
        """
        # 生成申请编号
        request_no = f"AR-{datetime.now().strftime('%Y%m%d%H%M%S')}-{uuid.uuid4().hex[:6].upper()}"

        # 获取审批链
        chain = None
        current_node_id = None
        current_approver_id = None

        if request_data.chain_id:
            chain = await self.get_chain(db, request_data.chain_id, include_nodes=True)
            if not chain:
                raise ValueError("指定的审批链不存在")
            if not chain.is_enabled:
                raise ValueError("指定的审批链已禁用")

            # 获取第一个节点
            if chain.nodes:
                sorted_nodes = sorted(chain.nodes, key=lambda x: x.node_order)
                first_node = sorted_nodes[0]
                current_node_id = first_node.id
                # 根据节点类型确定审批人
                current_approver_id = await self._resolve_approver(db, first_node)

        # 创建申请
        request = ApprovalRequest(
            request_no=request_no,
            business_type=request_data.business_type,
            chain_id=request_data.chain_id,
            applicant_id=applicant_id,
            title=request_data.title,
            content=request_data.content,
            attachments=request_data.attachments,
            current_node_id=current_node_id,
            current_approver_id=current_approver_id,
            status="pending",
            submitted_at=datetime.utcnow()
        )
        db.add(request)
        await db.commit()
        await db.refresh(request)

        return request

    async def approve(self, db: AsyncSession, request_id: int, approver_id: int,
                      approver_name: str = None, comment: str = None) -> ApprovalRequest:
        """
        审批通过

        Args:
            db: 数据库会话
            request_id: 申请ID
            approver_id: 审批人ID
            approver_name: 审批人姓名
            comment: 审批意见

        Returns:
            更新后的申请
        """
        request = await self.get_request(db, request_id, include_chain=True)
        if not request:
            raise ValueError("申请不存在")
        if request.status != "pending":
            raise ValueError("申请状态不是待审批")
        if request.current_approver_id != approver_id:
            raise ValueError("您不是当前审批人")

        # 记录审批
        record = ApprovalRecord(
            request_id=request_id,
            node_id=request.current_node_id,
            approver_id=approver_id,
            approver_name=approver_name,
            action="approve",
            comment=comment
        )
        db.add(record)

        # 移动到下一节点
        await self._move_to_next_node(db, request, approver_id)

        await db.commit()
        await db.refresh(request)
        return request

    async def reject(self, db: AsyncSession, request_id: int, approver_id: int,
                     approver_name: str = None, comment: str = None) -> ApprovalRequest:
        """
        审批拒绝

        Args:
            db: 数据库会话
            request_id: 申请ID
            approver_id: 审批人ID
            approver_name: 审批人姓名
            comment: 拒绝原因

        Returns:
            更新后的申请
        """
        request = await self.get_request(db, request_id)
        if not request:
            raise ValueError("申请不存在")
        if request.status != "pending":
            raise ValueError("申请状态不是待审批")
        if request.current_approver_id != approver_id:
            raise ValueError("您不是当前审批人")

        # 记录审批
        record = ApprovalRecord(
            request_id=request_id,
            node_id=request.current_node_id,
            approver_id=approver_id,
            approver_name=approver_name,
            action="reject",
            comment=comment
        )
        db.add(record)

        # 更新申请状态
        request.status = "rejected"
        request.completed_at = datetime.utcnow()

        await db.commit()
        await db.refresh(request)
        return request

    async def batch_approve(self, db: AsyncSession, request_ids: List[int],
                             approver_id: int, approver_name: str = None,
                             comment: str = None) -> Dict[str, Any]:
        """
        批量审批通过

        Args:
            db: 数据库会话
            request_ids: 申请ID列表
            approver_id: 审批人ID
            approver_name: 审批人姓名
            comment: 审批意见

        Returns:
            批量审批结果
        """
        success_count = 0
        failed_items = []

        for request_id in request_ids:
            try:
                await self.approve(db, request_id, approver_id, approver_name, comment)
                success_count += 1
            except Exception as e:
                failed_items.append({
                    "request_id": request_id,
                    "error": str(e)
                })

        return {
            "success": True,
            "total": len(request_ids),
            "success_count": success_count,
            "failed_count": len(failed_items),
            "failed_items": failed_items
        }

    # ========== 查询方法 ==========

    async def get_request(self, db: AsyncSession, request_id: int,
                           include_chain: bool = False,
                           include_records: bool = False) -> Optional[ApprovalRequest]:
        """
        获取审批申请

        Args:
            db: 数据库会话
            request_id: 申请ID
            include_chain: 是否包含审批链
            include_records: 是否包含审批记录

        Returns:
            审批申请
        """
        query = select(ApprovalRequest).where(ApprovalRequest.id == request_id)

        if include_chain:
            query = query.options(selectinload(ApprovalRequest.chain))
        if include_records:
            query = query.options(selectinload(ApprovalRequest.records))

        result = await db.execute(query)
        return result.scalar_one_or_none()

    async def list_requests(self, db: AsyncSession, query: ApprovalRequestQuery,
                             include_chain: bool = False) -> tuple[List[ApprovalRequest], int]:
        """
        列出审批申请

        Args:
            db: 数据库会话
            query: 查询参数
            include_chain: 是否包含审批链

        Returns:
            (申请列表, 总数)
        """
        stmt = select(ApprovalRequest)

        # 条件过滤
        if query.business_type:
            stmt = stmt.where(ApprovalRequest.business_type == query.business_type)
        if query.request_no:
            stmt = stmt.where(ApprovalRequest.request_no == query.request_no)
        if query.applicant_id:
            stmt = stmt.where(ApprovalRequest.applicant_id == query.applicant_id)
        if query.status:
            stmt = stmt.where(ApprovalRequest.status == query.status)
        if query.current_approver_id:
            stmt = stmt.where(ApprovalRequest.current_approver_id == query.current_approver_id)

        # 统计总数
        count_stmt = select(func.count()).select_from(stmt.subquery())
        total_result = await db.execute(count_stmt)
        total = total_result.scalar() or 0

        # 分页
        offset = (query.page - 1) * query.page_size
        stmt = stmt.order_by(ApprovalRequest.id.desc()).offset(offset).limit(query.page_size)

        if include_chain:
            stmt = stmt.options(selectinload(ApprovalRequest.chain))

        result = await db.execute(stmt)
        requests = result.scalars().all()

        return list(requests), total

    async def query_user_requests(self, db: AsyncSession, user_id: int,
                                   query: ApprovalRequestQuery) -> tuple[List[ApprovalRequest], int]:
        """
        查询用户的申请记录

        Args:
            db: 数据库会话
            user_id: 用户ID
            query: 查询参数

        Returns:
            (申请列表, 总数)
        """
        query.applicant_id = user_id
        return await self.list_requests(db, query)

    async def query_pending_approvals(self, db: AsyncSession, approver_id: int,
                                       query: ApprovalRequestQuery) -> tuple[List[ApprovalRequest], int]:
        """
        查询待审批的申请

        Args:
            db: 数据库会话
            approver_id: 审批人ID
            query: 查询参数

        Returns:
            (申请列表, 总数)
        """
        query.current_approver_id = approver_id
        query.status = "pending"
        return await self.list_requests(db, query, include_chain=True)

    # ========== 辅助方法 ==========

    async def _resolve_approver(self, db: AsyncSession, node: ApprovalNode) -> Optional[int]:
        """
        根据节点类型解析审批人ID

        Args:
            db: 数据库会话
            node: 审批节点

        Returns:
            审批人ID
        """
        from app.models import User

        if node.node_type == "user":
            # 直接指定用户ID
            try:
                return int(node.node_value)
            except ValueError:
                return None

        elif node.node_type == "role":
            # 根据角色查找用户
            result = await db.execute(
                select(User).where(User.role == node.node_value).limit(1)
            )
            user = result.scalar_one_or_none()
            return user.id if user else None

        elif node.node_type == "department_head":
            # 查找部门负责人（简化逻辑，实际可能更复杂）
            result = await db.execute(
                select(User).where(User.position.like("%负责人%")).limit(1)
            )
            user = result.scalar_one_or_none()
            return user.id if user else None

        return None

    async def _move_to_next_node(self, db: AsyncSession, request: ApprovalRequest,
                                 current_approver_id: int):
        """
        将申请移动到下一个审批节点

        Args:
            db: 数据库会话
            request: 审批申请
            current_approver_id: 当前审批人ID
        """
        if not request.chain_id or not request.chain:
            # 没有审批链，直接完成
            request.status = "approved"
            request.completed_at = datetime.utcnow()
            return

        # 获取审批链的节点
        result = await db.execute(
            select(ApprovalNode)
            .where(ApprovalNode.chain_id == request.chain_id)
            .order_by(ApprovalNode.node_order)
        )
        nodes = list(result.scalars().all())

        if not nodes:
            request.status = "approved"
            request.completed_at = datetime.utcnow()
            return

        # 找到当前节点
        current_node_index = None
        for i, node in enumerate(nodes):
            if node.id == request.current_node_id:
                current_node_index = i
                break

        if current_node_index is None or current_node_index >= len(nodes) - 1:
            # 没有下一个节点，审批完成
            request.status = "approved"
            request.completed_at = datetime.utcnow()
            request.current_node_id = None
            request.current_approver_id = None
            return

        # 处理会签模式
        current_node = nodes[current_node_index]
        if current_node.approval_mode == "and":
            # 会签模式：需要所有节点都通过
            # 检查当前节点的所有审批是否都通过了
            result = await db.execute(
                select(ApprovalRecord).where(
                    and_(
                        ApprovalRecord.request_id == request.id,
                        ApprovalRecord.node_id == current_node.id,
                        ApprovalRecord.action == "approve"
                    )
                )
            )
            records = result.scalars().all()

            # 统计需要审批的人数（简化处理）
            # 实际应该查询该节点有多少个审批人
            required_count = 1  # 简化处理

            if len(records) < required_count:
                # 还有人没审批，等待
                return

        # 移动到下一个节点
        next_node = nodes[current_node_index + 1]
        request.current_node_id = next_node.id
        request.current_approver_id = await self._resolve_approver(db, next_node)

    # ========== 催办功能 ==========

    async def create_reminder(self, db: AsyncSession, request_id: int,
                               requester_id: int) -> ApprovalReminder:
        """
        创建催办记录

        Args:
            db: 数据库会话
            request_id: 申请ID
            requester_id: 催办人ID

        Returns:
            催办记录
        """
        request = await self.get_request(db, request_id)
        if not request:
            raise ValueError("申请不存在")
        if request.status != "pending":
            raise ValueError("申请不是待审批状态")

        # 检查是否已存在催办记录
        result = await db.execute(
            select(ApprovalReminder).where(
                and_(
                    ApprovalReminder.request_id == request_id,
                    ApprovalReminder.requester_id == requester_id
                )
            )
        )
        existing = result.scalar_one_or_none()

        if existing:
            # 更新催办次数
            existing.reminder_count += 1
            existing.last_reminded_at = datetime.utcnow()
            await db.commit()
            await db.refresh(existing)
            return existing
        else:
            # 创建新催办记录
            reminder = ApprovalReminder(
                request_id=request_id,
                requester_id=requester_id
            )
            db.add(reminder)
            await db.commit()
            await db.refresh(reminder)
            return reminder

    async def get_records(self, db: AsyncSession, request_id: int) -> List[ApprovalRecord]:
        """
        获取申请的所有审批记录

        Args:
            db: 数据库会话
            request_id: 申请ID

        Returns:
            审批记录列表
        """
        result = await db.execute(
            select(ApprovalRecord)
            .where(ApprovalRecord.request_id == request_id)
            .order_by(ApprovalRecord.created_at)
        )
        return list(result.scalars().all())


# 全局服务实例
approval_service = ApprovalService()
