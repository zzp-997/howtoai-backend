"""
操作日志审计服务
记录用户关键操作，便于安全审计和问题追溯
"""
from datetime import datetime
from typing import Optional, Dict, Any
import json
import logging
from flask import request, g
from app.extensions import db
from app.models.operation_log import OperationLog
from app.models.login_log import LoginLog

logger = logging.getLogger(__name__)


class AuditService:
    """操作日志审计服务"""

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
    def log_login(cls, user_id: int, status: str, ip_address: Optional[str] = None,
                  failure_reason: Optional[str] = None) -> bool:
        """
        记录登录日志

        Args:
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
                ip_address=ip_address or cls._get_client_ip(),
                status=status,
                failure_reason=failure_reason
            )
            db.session.add(log)
            db.session.commit()

            logger.info(f"登录日志记录成功: user_id={user_id}, status={status}")
            return True
        except Exception as e:
            logger.error(f"登录日志记录失败: {e}")
            db.session.rollback()
            return False

    @classmethod
    def log_operation(cls, action: str, resource_type: Optional[str] = None,
                      resource_id: Optional[int] = None, detail: Optional[Dict] = None,
                      user_id: Optional[int] = None) -> bool:
        """
        记录操作日志

        Args:
            action: 操作类型
            resource_type: 资源类型
            resource_id: 资源ID
            detail: 操作详情
            user_id: 用户ID（默认从上下文获取）

        Returns:
            是否记录成功
        """
        try:
            # 获取当前用户ID
            if user_id is None:
                user_id = getattr(g, 'user_id', None)

            if user_id is None:
                logger.warning(f"无法记录操作日志：用户ID为空，action={action}")
                return False

            log = OperationLog(
                user_id=user_id,
                action=action,
                resource_type=resource_type,
                resource_id=resource_id,
                detail=json.dumps(detail, ensure_ascii=False) if detail else None,
                ip_address=cls._get_client_ip(),
                user_agent=cls._get_user_agent()
            )
            db.session.add(log)
            db.session.commit()

            logger.debug(f"操作日志记录成功: user_id={user_id}, action={action}")
            return True
        except Exception as e:
            logger.error(f"操作日志记录失败: {e}")
            db.session.rollback()
            return False

    @classmethod
    def log_sensitive_operation(cls, action: str, resource_type: str,
                                 resource_id: int, detail: Dict[str, Any]) -> bool:
        """
        记录敏感操作日志（强制记录）

        Args:
            action: 操作类型
            resource_type: 资源类型
            resource_id: 资源ID
            detail: 操作详情

        Returns:
            是否记录成功
        """
        # 标记为敏感操作
        detail['_sensitive'] = True
        return cls.log_operation(action, resource_type, resource_id, detail)

    @classmethod
    def query_user_logs(cls, user_id: int, action: Optional[str] = None,
                        start_time: Optional[datetime] = None,
                        end_time: Optional[datetime] = None,
                        page: int = 1, page_size: int = 20) -> Dict:
        """
        查询用户操作日志

        Args:
            user_id: 用户ID
            action: 操作类型（可选）
            start_time: 开始时间（可选）
            end_time: 结束时间（可选）
            page: 页码
            page_size: 每页数量

        Returns:
            分页结果
        """
        query = OperationLog.query.filter(OperationLog.user_id == user_id)

        if action:
            query = query.filter(OperationLog.action == action)

        if start_time:
            query = query.filter(OperationLog.created_at >= start_time)

        if end_time:
            query = query.filter(OperationLog.created_at <= end_time)

        query = query.order_by(OperationLog.created_at.desc())

        pagination = query.paginate(page=page, per_page=page_size, error_out=False)

        return {
            "items": [log.to_dict() for log in pagination.items],
            "total": pagination.total,
            "page": page,
            "page_size": page_size,
            "pages": pagination.pages
        }

    @classmethod
    def query_resource_logs(cls, resource_type: str, resource_id: int,
                            page: int = 1, page_size: int = 20) -> Dict:
        """
        查询资源操作日志

        Args:
            resource_type: 资源类型
            resource_id: 资源ID
            page: 页码
            page_size: 每页数量

        Returns:
            分页结果
        """
        query = OperationLog.query.filter(
            OperationLog.resource_type == resource_type,
            OperationLog.resource_id == resource_id
        ).order_by(OperationLog.created_at.desc())

        pagination = query.paginate(page=page, per_page=page_size, error_out=False)

        return {
            "items": [log.to_dict() for log in pagination.items],
            "total": pagination.total,
            "page": page,
            "page_size": page_size,
            "pages": pagination.pages
        }

    @classmethod
    def query_login_logs(cls, user_id: Optional[int] = None,
                         status: Optional[str] = None,
                         start_time: Optional[datetime] = None,
                         end_time: Optional[datetime] = None,
                         page: int = 1, page_size: int = 20) -> Dict:
        """
        查询登录日志

        Args:
            user_id: 用户ID（可选）
            status: 状态（可选）
            start_time: 开始时间（可选）
            end_time: 结束时间（可选）
            page: 页码
            page_size: 每页数量

        Returns:
            分页结果
        """
        query = LoginLog.query

        if user_id:
            query = query.filter(LoginLog.user_id == user_id)

        if status:
            query = query.filter(LoginLog.status == status)

        if start_time:
            query = query.filter(LoginLog.created_at >= start_time)

        if end_time:
            query = query.filter(LoginLog.created_at <= end_time)

        query = query.order_by(LoginLog.created_at.desc())

        pagination = query.paginate(page=page, per_page=page_size, error_out=False)

        return {
            "items": [log.to_dict() for log in pagination.items],
            "total": pagination.total,
            "page": page,
            "page_size": page_size,
            "pages": pagination.pages
        }

    @staticmethod
    def _get_client_ip() -> str:
        """获取客户端真实IP"""
        if request.headers.get('X-Forwarded-For'):
            return request.headers.get('X-Forwarded-For').split(',')[0].strip()
        elif request.headers.get('X-Real-IP'):
            return request.headers.get('X-Real-IP')
        return request.remote_addr or "unknown"

    @staticmethod
    def _get_user_agent() -> str:
        """获取User-Agent"""
        return request.headers.get('User-Agent', '')[:500]


def audit_decorator(action: str, resource_type: Optional[str] = None):
    """
    操作审计装饰器

    Args:
        action: 操作类型
        resource_type: 资源类型
    """
    def decorator(f):
        from functools import wraps
        @wraps(f)
        def decorated_function(*args, **kwargs):
            # 执行原函数
            result = f(*args, **kwargs)

            # 记录审计日志
            resource_id = kwargs.get('id') or kwargs.get('resource_id')
            AuditService.log_operation(action, resource_type, resource_id)

            return result
        return decorated_function
    return decorator
