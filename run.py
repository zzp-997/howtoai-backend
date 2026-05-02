"""
启动脚本
"""
import os
# Windows 上 slowapi 读取 .env 需要 UTF-8 编码
os.environ.setdefault("PYTHONUTF8", "1")

import uvicorn
from app.core.config import settings

if __name__ == "__main__":
    uvicorn.run(
        "app.main:app",
        host="0.0.0.0",
        port=8000,
        reload=settings.DEBUG
    )