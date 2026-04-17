"""
应用配置
"""
from pydantic_settings import BaseSettings
from typing import List
import json


class Settings(BaseSettings):
    """应用配置类"""
    # 数据库
    DATABASE_URL: str

    # JWT
    SECRET_KEY: str = "your-super-secret-key-change-in-production"
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 1440  # 24小时

    # 应用
    APP_NAME: str = "极智协同 API"
    APP_VERSION: str = "1.0.0"
    DEBUG: bool = True

    # 跨域
    CORS_ORIGINS: str = '["http://localhost:5173", "http://localhost:3000", "http://localhost:3003"]'

    @property
    def cors_origins_list(self) -> List[str]:
        """获取跨域列表"""
        try:
            origins = json.loads(self.CORS_ORIGINS)
            # 开发模式下允许所有 localhost
            if self.DEBUG:
                origins.append("*")
            return origins
        except:
            return ["*"]

    class Config:
        env_file = ".env"
        extra = "ignore"


# 全局配置实例
settings = Settings()
