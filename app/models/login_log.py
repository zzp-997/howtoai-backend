"""
登录日志模型
"""
from datetime import datetime
from app.extensions import db


class LoginLog(db.Model):
    """登录日志表"""
    __tablename__ = 'login_logs'

    id = db.Column(db.BigInteger, primary_key=True, autoincrement=True)
    user_id = db.Column(db.BigInteger, nullable=False, index=True, comment='用户ID')
    ip_address = db.Column(db.String(45), comment='IP地址')
    status = db.Column(db.Enum('success', 'failed'), nullable=False, comment='登录状态')
    failure_reason = db.Column(db.String(100), comment='失败原因')
    created_at = db.Column(db.DateTime, default=datetime.utcnow, comment='创建时间')

    # 索引
    __table_args__ = (
        db.Index('idx_user_status_time', 'user_id', 'status', 'created_at'),
        {'comment': '登录日志表'}
    )

    def to_dict(self):
        """转换为字典"""
        return {
            'id': self.id,
            'user_id': self.user_id,
            'ip_address': self.ip_address,
            'status': self.status,
            'failure_reason': self.failure_reason,
            'created_at': self.created_at.isoformat() if self.created_at else None
        }

    def __repr__(self):
        return f'<LoginLog {self.id}: user={self.user_id} status={self.status}>'
