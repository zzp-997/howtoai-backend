"""
文档相关 Schema
"""
import json
from pydantic import BaseModel, field_validator
from typing import Optional, List
from datetime import datetime


class DocumentCategoryBase(BaseModel):
    """文档分类基础"""
    name: str
    description: Optional[str] = None


class DocumentCategoryCreate(DocumentCategoryBase):
    """创建文档分类"""
    pass


class DocumentCategoryResponse(DocumentCategoryBase):
    """文档分类响应"""
    id: int
    createdAt: Optional[datetime] = None

    class Config:
        from_attributes = True


class DocumentBase(BaseModel):
    """文档基础"""
    categoryId: Optional[int] = None
    name: str
    description: Optional[str] = None
    tags: Optional[List[str]] = None


class DocumentCreate(DocumentBase):
    """创建文档"""
    fileSize: Optional[int] = None
    fileType: Optional[str] = None


class DocumentResponse(DocumentBase):
    """文档响应"""
    id: int
    fileSize: Optional[int] = None
    fileType: Optional[str] = None
    uploadBy: Optional[int] = None
    createdAt: Optional[datetime] = None

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

    class Config:
        from_attributes = True