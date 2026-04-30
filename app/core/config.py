"""
应用配置
"""
from pydantic_settings import BaseSettings
from typing import List
import json
import os


def get_env_file() -> str:
    """获取环境配置文件路径，优先使用 .env.local"""
    local_env = ".env.local"
    if os.path.exists(local_env):
        return local_env
    return ".env"


class Settings(BaseSettings):
    """应用配置类"""
    # 数据库
    DATABASE_URL: str

    # JWT
    SECRET_KEY: str = "your-super-secret-key-change-in-production"
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 120  # 2小时
    REFRESH_TOKEN_EXPIRE_DAYS: int = 7  # 7天

    # 应用
    APP_NAME: str = "极智协同 API"
    APP_VERSION: str = "1.0.0"
    DEBUG: bool = True

    # 跨域
    CORS_ORIGINS: str = '["http://localhost:5173", "http://localhost:3000", "http://localhost:3003"]'

    # Redis（可选）
    REDIS_URL: str = "redis://localhost:6379/0"
    REDIS_ENABLED: bool = False

    # 安全配置 - 登录失败限制
    LOGIN_FAIL_THRESHOLD: int = 5  # 连续失败次数阈值
    LOGIN_LOCK_DURATION_MINUTES: int = 15  # 锁定时长（分钟）
    LOGIN_FAIL_WINDOW_MINUTES: int = 30  # 失败计数窗口（分钟）

    # 安全配置 - 请求频率限制
    RATE_LIMIT_GLOBAL: int = 1000  # 全局IP限制（次/分钟）
    RATE_LIMIT_USER: int = 100  # 用户级限制（次/分钟）
    RATE_LIMIT_LOGIN: int = 10  # 登录接口限制（次/分钟）
    RATE_LIMIT_SENSITIVE: int = 20  # 敏感操作限制（次/小时）

    # 安全配置 - 密码策略
    PASSWORD_MIN_LENGTH: int = 8
    PASSWORD_REQUIRE_UPPERCASE: bool = True
    PASSWORD_REQUIRE_LOWERCASE: bool = True
    PASSWORD_REQUIRE_DIGIT: bool = True
    PASSWORD_REQUIRE_SPECIAL: bool = False
    PASSWORD_EXPIRE_DAYS: int = 90  # 密码过期天数
    PASSWORD_HISTORY_COUNT: int = 5  # 历史密码检查数量

    @property
    def cors_origins_list(self) -> List[str]:
        """获取跨域列表"""
        try:
            origins = json.loads(self.CORS_ORIGINS)
            if self.DEBUG:
                origins.append("*")
            return origins
        except:
            return ["*"]

    class Config:
        env_file = get_env_file()
        extra = "ignore"


# 全局配置实例
settings = Settings()
