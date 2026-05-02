"""
操作日志审计服务 - 异步版本
记录用户关键操作，便于安全审计和问题追溯

使用 SQLAlchemy AsyncSession 替代 Flask-SQLAlchemy
"""
from datetime import datetime
from typing import Optional, Dict, Any
import json
import logging
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func, desc
from app.models.operation_log import OperationLog
from app.models.login_log import LoginLog

logger = logging.getLogger(__name__)


class AuditServiceV2:
    """操作日志审计服务 - 异步版本"""

    # 需要记录的敏感操作配置
    AUDIT_ACTIONS = {
        # 认证操作
        "login": {"type": "auth", "description": "用户登录"},
        "logout": {"type": "auth", "description": "用户登出"},
        "token_refresh": {"type": "auth", "description": "Token刷新"},
        "password_change": {"type": "auth", "description": "密码修改"},

        # 审批操作
        "application_submit": {"type": "approval", "description": "提交申请"},
        "application_approve": {"type": "approval", "description": "审批通过"},
        "application_reject": {"type": "approval", "description": "审批拒绝"},
        "application_revoke": {"type": "approval", "description": "撤销申请"},

        # 数据操作
        "user_create": {"type": "data", "description": "创建用户"},
        "user_update": {"type": "data", "description": "更新用户"},
        "user_delete": {"type": "data", "description": "删除用户"},
        "role_change": {"type": "data", "description": "角色变更"},
        "permission_change": {"type": "data", "description": "权限调整"},

        # 系统操作
        "system_config_change": {"type": "system", "description": "系统配置变更"},
        "data_export": {"type": "system", "description": "数据导出"},
    }

    @classmethod
    async def log_login(cls, db: AsyncSession, user_id: int, status: str,
                        ip_address: Optional[str] = None,
                        failure_reason: Optional[str] = None) -> bool:
        """
        记录登录日志

        Args:
            db: 数据库会话
            user_id: 用户ID
            status: 状态 ('success' | 'failed')
            ip_address: IP地址
            failure_reason: 失败原因

        Returns:
            是否记录成功
        """
        try:
            log = LoginLog(
                user_id=user_id,
                ip_address=ip_address or "unknown",
                status=status,
                failure_reason=failure_reason
            )
            db.add(log)
            await db.commit()

            logger.info(f"登录日志记录成功: user_id={user_id}, status={status}")
            return True
        except Exception as e:
            logger.error(f"登录日志记录失败: {e}")
            await db.rollback()
            return False

    @classmethod
    async def log_operation(cls, db: AsyncSession, action: str,
                           resource_type: Optional[str] = None,
                           resource_id: Optional[int] = None,
                           detail: Optional[Dict] = None,
                           user_id: Optional[int] = None,
                           ip_address: Optional[str] = None,
                           user_agent: Optional[str] = None) -> bool:
        """
        记录操作日志

        Args:
            db: 数据库会话
            action: 操作类型
            resource_type: 资源类型
            resource_id: 资源ID
            detail: 操作详情
            user_id: 用户ID
            ip_address: IP地址（可选）
            user_agent: User-Agent（可选）

        Returns:
            是否记录成功
        """
        try:
            if user_id is None:
                logger.warning(f"无法记录操作日志：用户ID为空，action={action}")
                return False

            log = OperationLog(
                user_id=user_id,
                action=action,
                resource_type=resource_type,
                resource_id=resource_id,
                detail=json.dumps(detail, ensure_ascii=False) if detail else None,
                ip_address=ip_address or "unknown",
                user_agent=user_agent or ""
            )
            db.add(log)
            await db.commit()

            logger.debug(f"操作日志记录成功: user_id={user_id}, action={action}")
            return True
        except Exception as e:
            logger.error(f"操作日志记录失败: {e}")
            await db.rollback()
            return False

    @classmethod
    async def log_sensitive_operation(cls, db: AsyncSession, action: str,
                                       resource_type: str, resource_id: int,
                                       detail: Dict[str, Any],
                                       user_id: Optional[int] = None,
                                       ip_address: Optional[str] = None,
                                       user_agent: Optional[str] = None) -> bool:
        """
        记录敏感操作日志（强制记录）

        Args:
            db: 数据库会话
            action: 操作类型
            resource_type: 资源类型
            resource_id: 资源ID
            detail: 操作详情
            user_id: 用户ID（可选）
            ip_address: IP地址（可选）
            user_agent: User-Agent（可选）

        Returns:
            是否记录成功
        """
        # 标记为敏感操作
        detail['_sensitive'] = True
        return await cls.log_operation(
            db, action, resource_type, resource_id, detail,
            user_id, ip_address, user_agent
        )

    @classmethod
    async def query_user_logs(cls, db: AsyncSession, user_id: int,
                              action: Optional[str] = None,
                              start_time: Optional[datetime] = None,
                              end_time: Optional[datetime] = None,
                              page: int = 1, page_size: int = 20) -> Dict:
        """
        查询用户操作日志

        Args:
            db: 数据库会话
            user_id: 用户ID
            action: 操作类型（可选）
            start_time: 开始时间（可选）
            end_time: 结束时间（可选）
            page: 页码
            page_size: 每页数量

        Returns:
            分页结果
        """
        # 构建查询
        conditions = [OperationLog.user_id == user_id]

        if action:
            conditions.append(OperationLog.action == action)

        if start_time:
            conditions.append(OperationLog.created_at >= start_time)

        if end_time:
            conditions.append(OperationLog.created_at <= end_time)

        # 查询总数
        count_query = select(func.count()).select_from(OperationLog).where(*conditions)
        total_result = await db.execute(count_query)
        total = total_result.scalar() or 0

        # 计算分页
        offset = (page - 1) * page_size
        total_pages = (total + page_size - 1) // page_size if total > 0 else 0

        # 查询数据
        query = (
            select(OperationLog)
            .where(*conditions)
            .order_by(desc(OperationLog.created_at))
            .offset(offset)
            .limit(page_size)
        )
        result = await db.execute(query)
        logs = result.scalars().all()

        return {
            "items": [log.to_dict() for log in logs],
            "total": total,
            "page": page,
            "page_size": page_size,
            "pages": total_pages
        }

    @classmethod
    async def query_resource_logs(cls, db: AsyncSession, resource_type: str,
                                  resource_id: int,
                                  page: int = 1, page_size: int = 20) -> Dict:
        """
        查询资源操作日志

        Args:
            db: 数据库会话
            resource_type: 资源类型
            resource_id: 资源ID
            page: 页码
            page_size: 每页数量

        Returns:
            分页结果
        """
        conditions = [
            OperationLog.resource_type == resource_type,
            OperationLog.resource_id == resource_id
        ]

        # 查询总数
        count_query = select(func.count()).select_from(OperationLog).where(*conditions)
        total_result = await db.execute(count_query)
        total = total_result.scalar() or 0

        # 计算分页
        offset = (page - 1) * page_size
        total_pages = (total + page_size - 1) // page_size if total > 0 else 0

        # 查询数据
        query = (
            select(OperationLog)
            .where(*conditions)
            .order_by(desc(OperationLog.created_at))
            .offset(offset)
            .limit(page_size)
        )
        result = await db.execute(query)
        logs = result.scalars().all()

        return {
            "items": [log.to_dict() for log in logs],
            "total": total,
            "page": page,
            "page_size": page_size,
            "pages": total_pages
        }

    @classmethod
    async def query_login_logs(cls, db: AsyncSession,
                               user_id: Optional[int] = None,
                               status: Optional[str] = None,
                               start_time: Optional[datetime] = None,
                               end_time: Optional[datetime] = None,
                               page: int = 1, page_size: int = 20) -> Dict:
        """
        查询登录日志

        Args:
            db: 数据库会话
            user_id: 用户ID（可选）
            status: 状态（可选）
            start_time: 开始时间（可选）
            end_time: 结束时间（可选）
            page: 页码
            page_size: 每页数量

        Returns:
            分页结果
        """
        conditions = []

        if user_id:
            conditions.append(LoginLog.user_id == user_id)

        if status:
            conditions.append(LoginLog.status == status)

        if start_time:
            conditions.append(LoginLog.created_at >= start_time)

        if end_time:
            conditions.append(LoginLog.created_at <= end_time)

        # 查询总数
        count_query = select(func.count()).select_from(LoginLog).where(*conditions)
        total_result = await db.execute(count_query)
        total = total_result.scalar() or 0

        # 计算分页
        offset = (page - 1) * page_size
        total_pages = (total + page_size - 1) // page_size if total > 0 else 0

        # 查询数据
        query = (
            select(LoginLog)
            .where(*conditions)
            .order_by(desc(LoginLog.created_at))
            .offset(offset)
            .limit(page_size)
        )
        result = await db.execute(query)
        logs = result.scalars().all()

        return {
            "items": [log.to_dict() for log in logs],
            "total": total,
            "page": page,
            "page_size": page_size,
            "pages": total_pages
        }


# 全局服务实例（向后兼容）
audit_service_v2 = AuditServiceV2()
