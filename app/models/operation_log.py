"""
操作日志模型
"""
from datetime import datetime
from app.extensions import db


class OperationLog(db.Model):
    """操作日志表"""
    __tablename__ = 'operation_logs'

    id = db.Column(db.BigInteger, primary_key=True, autoincrement=True)
    user_id = db.Column(db.BigInteger, nullable=False, index=True, comment='用户ID')
    action = db.Column(db.String(50), nullable=False, comment='操作类型')
    resource_type = db.Column(db.String(50), comment='资源类型')
    resource_id = db.Column(db.BigInteger, comment='资源ID')
    detail = db.Column(db.JSON, comment='操作详情')
    ip_address = db.Column(db.String(45), comment='IP地址')
    user_agent = db.Column(db.String(500), comment='User-Agent')
    created_at = db.Column(db.DateTime, default=datetime.utcnow, comment='创建时间')

    # 索引
    __table_args__ = (
        db.Index('idx_user_action_time', 'user_id', 'action', 'created_at'),
        db.Index('idx_resource', 'resource_type', 'resource_id'),
        {'comment': '操作日志表'}
    )

    def to_dict(self):
        """转换为字典"""
        return {
            'id': self.id,
            'user_id': self.user_id,
            'action': self.action,
            'resource_type': self.resource_type,
            'resource_id': self.resource_id,
            'detail': self.detail,
            'ip_address': self.ip_address,
            'user_agent': self.user_agent,
            'created_at': self.created_at.isoformat() if self.created_at else None
        }

    def __repr__(self):
        return f'<OperationLog {self.id}: user={self.user_id} action={self.action}>'
