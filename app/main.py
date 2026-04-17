"""
极智协同 FastAPI 后端
"""
from fastapi import FastAPI, Request, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from fastapi.exceptions import RequestValidationError
from app.core.config import settings
from app.api import api_router
from app.init_data import create_tables, init_data
from app.schemas.common import ResponseModel


# 创建应用
app = FastAPI(
    title=settings.APP_NAME,
    version=settings.APP_VERSION,
    description="极智协同办公系统后端 API",
    debug=settings.DEBUG
)


# ==================== 统一异常处理 ====================

@app.exception_handler(HTTPException)
async def http_exception_handler(request: Request, exc: HTTPException):
    """处理 FastAPI HTTP 异常"""
    return JSONResponse(
        status_code=exc.status_code,
        content={
            "code": exc.status_code,
            "message": exc.detail,
            "data": None
        }
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

    return JSONResponse(
        status_code=422,
        content={
            "code": 422,
            "message": msg,
            "data": None
        }
    )


@app.exception_handler(Exception)
async def general_exception_handler(request: Request, exc: Exception):
    """处理未知异常"""
    return JSONResponse(
        status_code=500,
        content={
            "code": 500,
            "message": str(exc) if settings.DEBUG else "服务器内部错误",
            "data": None
        }
    )


# ==================== 跨域配置 ====================

app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.cors_origins_list,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# ==================== 注册路由 ====================

app.include_router(api_router, prefix="/api")


# ==================== 启动事件 ====================

@app.on_event("startup")
async def startup_event():
    """启动时初始化"""
    await create_tables()
    await init_data()


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
