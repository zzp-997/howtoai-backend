"""
通用响应 Schema
"""
from pydantic import BaseModel
from typing import Generic, TypeVar, Optional

T = TypeVar("T")


class ResponseModel(BaseModel, Generic[T]):
    """通用响应模型"""
    code: int = 200
    message: str = "success"
    data: Optional[T] = None


class PaginationModel(BaseModel, Generic[T]):
    """分页响应模型"""
    items: list[T]
    total: int
    page: int
    pageSize: int