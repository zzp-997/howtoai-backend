"""
知识库相关 Schema
"""
from pydantic import BaseModel
from typing import Optional, List
from datetime import datetime
from app.schemas.common import CamelModel


# ============ KnowledgeCategory 知识分类 ============

class KnowledgeCategoryBase(CamelModel):
    """知识分类基础"""
    name: str
    parent_id: Optional[int] = None
    level: Optional[int] = 1
    sort_order: Optional[int] = 0


class KnowledgeCategoryCreate(KnowledgeCategoryBase):
    """创建知识分类"""
    pass


class KnowledgeCategoryUpdate(CamelModel):
    """更新知识分类"""
    name: Optional[str] = None
    parent_id: Optional[int] = None
    sort_order: Optional[int] = None


class KnowledgeCategoryResponse(KnowledgeCategoryBase):
    """知识分类响应"""
    id: int
    created_by: Optional[int] = None
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None
    children: Optional[List["KnowledgeCategoryResponse"]] = None


# ============ KnowledgeArticle 知识文章 ============

class KnowledgeArticleBase(CamelModel):
    """知识文章基础"""
    title: str
    summary: Optional[str] = None
    content: Optional[str] = None
    category_id: Optional[int] = None
    tags: Optional[List[str]] = None
    status: Optional[str] = "draft"


class KnowledgeArticleCreate(KnowledgeArticleBase):
    """创建知识文章"""
    pass


class KnowledgeArticleUpdate(CamelModel):
    """更新知识文章"""
    title: Optional[str] = None
    summary: Optional[str] = None
    content: Optional[str] = None
    category_id: Optional[int] = None
    tags: Optional[List[str]] = None
    status: Optional[str] = None


class KnowledgeArticleResponse(KnowledgeArticleBase):
    """知识文章响应"""
    id: int
    author_id: Optional[int] = None
    author_name: Optional[str] = None
    category_name: Optional[str] = None
    view_count: int = 0
    like_count: int = 0
    is_liked: Optional[bool] = False
    published_at: Optional[datetime] = None
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None


class KnowledgeArticleListResponse(CamelModel):
    """知识文章列表响应"""
    items: List[KnowledgeArticleResponse]
    total: int
    page: int
    page_size: int


# ============ 搜索相关 ============

class KnowledgeSearchQuery(CamelModel):
    """知识库搜索查询"""
    keyword: str
    category_id: Optional[int] = None
    tags: Optional[List[str]] = None
    author_id: Optional[int] = None
    status: Optional[str] = "published"
    page: int = 1
    page_size: int = 20


class KnowledgeSearchResult(CamelModel):
    """知识库搜索结果"""
    id: int
    title: str
    summary: Optional[str] = None
    category_name: Optional[str] = None
    author_name: Optional[str] = None
    view_count: int = 0
    published_at: Optional[datetime] = None
    highlight: Optional[str] = None  # 高亮片段


# ============ 点赞/阅读 ============

class KnowledgeArticleLikeResponse(CamelModel):
    """点赞响应"""
    article_id: int
    is_liked: bool
    like_count: int


class KnowledgeArticleViewResponse(CamelModel):
    """阅读记录响应"""
    article_id: int
    view_count: int
    is_viewed: bool


# 更新前向引用
KnowledgeCategoryResponse.model_rebuild()
