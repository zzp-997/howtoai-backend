"""
通用响应 Schema
"""
from pydantic import BaseModel, ConfigDict
from pydantic.alias_generators import to_camel
from typing import Generic, TypeVar, Optional

T = TypeVar("T")


class CamelModel(BaseModel):
    """自动转换 camelCase 的基础模型
    Python 字段用 snake_case，API 自动序列化为 camelCase
    """
    model_config = ConfigDict(
        from_attributes=True,
        populate_by_name=True,
        alias_generator=to_camel
    )


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
    page_size: int
