"""
文档相关 Schema
"""
import json
from pydantic import field_validator
from typing import Optional, List
from datetime import datetime
from app.schemas.common import CamelModel


class DocumentCategoryBase(CamelModel):
    """文档分类基础"""
    name: str
    description: Optional[str] = None


class DocumentCategoryCreate(DocumentCategoryBase):
    """创建文档分类"""
    pass


class DocumentCategoryResponse(DocumentCategoryBase):
    """文档分类响应"""
    id: int
    created_at: Optional[datetime] = None


class DocumentBase(CamelModel):
    """文档基础"""
    category_id: Optional[int] = None
    name: str
    description: Optional[str] = None
    tags: Optional[List[str]] = None


class DocumentCreate(DocumentBase):
    """创建文档"""
    file_size: Optional[int] = None
    file_type: Optional[str] = None


class DocumentResponse(DocumentBase):
    """文档响应"""
    id: int
    file_size: Optional[int] = None
    file_type: Optional[str] = None
    upload_by: Optional[int] = None
    created_at: Optional[datetime] = None

    @field_validator('tags', mode='before')
    @classmethod
    def parse_tags(cls, v):
        """解析 tags 字段，支持 JSON 字符串"""
        if v is None:
            return []
        if isinstance(v, list):
            return v
        if isinstance(v, str):
            try:
                return json.loads(v)
            except:
                return []
        return []
