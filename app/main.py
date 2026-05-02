"""
极智协同 FastAPI 后端
"""
import os
from pathlib import Path
from fastapi import FastAPI, Request, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from fastapi.exceptions import RequestValidationError
from app.core.config import settings
from app.schemas.common import ResponseModel
from app.core.exceptions import BizException
from app.core.redis_client import redis_client
from app.core.security_module.rate_limit_middleware_fastapi import RateLimitMiddleware


# 创建应用
app = FastAPI(
    title=settings.APP_NAME,
    version=settings.APP_VERSION,
    description="极智协同办公系统后端 API",
    debug=settings.DEBUG
)


# ==================== 统一异常处理 ====================

def _build_cors_headers(request: Request) -> dict:
    """构建CORS响应头"""
    origin = request.headers.get("origin", "")
    allow_origins = settings.cors_origins_list
    if origin and (origin in allow_origins or "*" in allow_origins):
        return {
            "Access-Control-Allow-Origin": origin if origin in allow_origins else "*",
            "Access-Control-Allow-Methods": "DELETE, GET, HEAD, OPTIONS, PATCH, POST, PUT",
            "Access-Control-Allow-Headers": "Content-Type, Authorization, X-Requested-With",
            "Access-Control-Allow-Credentials": "true",
            "Access-Control-Max-Age": "600",
            "Vary": "Origin",
        }
    return {}


@app.exception_handler(BizException)
async def biz_exception_handler(request: Request, exc: BizException):
    """处理业务异常 — HTTP 200 + body.code，前端统一走 transformRequestHook 处理"""
    headers = _build_cors_headers(request)
    return JSONResponse(
        status_code=200,
        content={
            "code": exc.code,
            "message": exc.message,
            "data": None
        },
        headers=headers,
    )


@app.exception_handler(HTTPException)
async def http_exception_handler(request: Request, exc: HTTPException):
    """处理 FastAPI HTTP 异常"""
    headers = _build_cors_headers(request)
    return JSONResponse(
        status_code=exc.status_code,
        content={
            "code": exc.status_code,
            "message": exc.detail,
            "data": None
        },
        headers=headers,
    )


@app.exception_handler(RequestValidationError)
async def validation_exception_handler(request: Request, exc: RequestValidationError):
    """处理请求验证错误"""
    errors = exc.errors()
    if errors:
        error = errors[0]
        field = ".".join(str(loc) for loc in error.get("loc", []) if loc != "body")
        msg = f"{field}: {error.get('msg', '参数错误')}" if field else error.get('msg', '参数错误')
    else:
        msg = "请求参数错误"

    headers = _build_cors_headers(request)
    return JSONResponse(
        status_code=422,
        content={
            "code": 422,
            "message": msg,
            "data": None
        },
        headers=headers,
    )


@app.exception_handler(Exception)
async def general_exception_handler(request: Request, exc: Exception):
    """处理未知异常"""
    headers = _build_cors_headers(request)
    return JSONResponse(
        status_code=500,
        content={
            "code": 500,
            "message": str(exc) if settings.DEBUG else "服务器内部错误",
            "data": None
        },
        headers=headers,
    )


# ==================== 跨域配置 ====================

app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.cors_origins_list,
    allow_credentials=True,
    allow_methods=["GET", "POST", "PUT", "DELETE", "PATCH", "OPTIONS"],
    allow_headers=[
        "Authorization",
        "Content-Type",
        "X-Requested-With",
        "Accept",
        "Origin",
        "Access-Control-Request-Method",
        "Access-Control-Request-Headers",
    ],
    expose_headers=["Content-Type", "Authorization"],
)


# ==================== 安全模块初始化 ====================

# 初始化限流中间件（必须在路由导入前）
# TODO: slowapi与FastAPI 0.115兼容性问题，临时禁用
RateLimitMiddleware.init_app(app)

# 导入并注册路由（延迟导入以避免装饰器求值时限流中间件未初始化）
from app.api import api_router


@app.on_event("startup")
async def startup_event():
    """启动时初始化安全模块"""
    # 连接Redis（如果启用）
    if settings.REDIS_ENABLED:
        await redis_client.connect()
    print(f"安全模块初始化完成 - Redis状态: {'已连接' if redis_client.is_connected() else '使用内存缓存'}")


@app.on_event("shutdown")
async def shutdown_event():
    """关闭时清理资源"""
    if redis_client.is_connected():
        await redis_client.disconnect()
    print("安全模块资源已释放")


# ==================== 注册路由 ====================

app.include_router(api_router, prefix="/api")


# ==================== 启动事件 ====================
# 注意：在 Vercel Serverless 环境中，不使用 startup 事件
# 数据库初始化应通过单独脚本执行：python -m app.init_data
# @app.on_event("startup")
# async def startup_event():
#     """启动时初始化"""
#     await create_tables()
#     await init_data()


# ==================== 健康检查 ====================

@app.get("/")
async def root():
    """根路径"""
    return ResponseModel(
        code=200,
        message="success",
        data={
            "name": settings.APP_NAME,
            "version": settings.APP_VERSION,
            "status": "running"
        }
    )


@app.get("/health")
async def health():
    """健康检查"""
    return ResponseModel(code=200, message="success", data={"status": "healthy"})


@app.get("/version")
async def version():
    """获取部署版本信息"""
    version_info = {
        "app_version": settings.APP_VERSION,
        "commit": "unknown",
        "message": "",
        "deploy_time": "",
        "deployer": ""
    }

    # 读取 VERSION 文件
    version_file = Path(__file__).parent.parent / "VERSION"
    if version_file.exists():
        try:
            content = version_file.read_text(encoding="utf-8")
            for line in content.strip().split("\n"):
                if ":" in line:
                    key, value = line.split(":", 1)
                    key = key.strip().replace(" ", "_")
                    if key in version_info:
                        version_info[key] = value.strip()
        except Exception:
            pass

    return ResponseModel(code=200, message="success", data=version_info)
