"""
知识库相关数据模型
"""
from sqlalchemy import Column, Integer, String, DateTime, Text, Boolean, JSON
from sqlalchemy.sql import func
from app.core.database import Base


class KnowledgeCategory(Base):
    """知识分类表"""
    __tablename__ = "knowledge_categories"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(100), nullable=False)
    parent_id = Column(Integer, index=True)
    level = Column(Integer, default=1)
    sort_order = Column(Integer, default=0)
    created_by = Column(Integer, index=True)
    created_at = Column(DateTime, server_default=func.now())
    updated_at = Column(DateTime, server_default=func.now(), onupdate=func.now())


class KnowledgeArticle(Base):
    """知识文章表"""
    __tablename__ = "knowledge_articles"

    id = Column(Integer, primary_key=True, index=True)
    title = Column(String(200), nullable=False)
    summary = Column(Text)
    content = Column(Text)
    category_id = Column(Integer, index=True)
    author_id = Column(Integer, index=True)
    tags = Column(Text)  # JSON数组存储
    view_count = Column(Integer, default=0)
    like_count = Column(Integer, default=0)
    status = Column(String(20), default="draft")  # draft/published/archived
    published_at = Column(DateTime)
    created_at = Column(DateTime, server_default=func.now())
    updated_at = Column(DateTime, server_default=func.now(), onupdate=func.now())


class KnowledgeArticleLike(Base):
    """知识文章点赞表"""
    __tablename__ = "knowledge_article_likes"

    id = Column(Integer, primary_key=True, index=True)
    article_id = Column(Integer, index=True, nullable=False)
    user_id = Column(Integer, index=True, nullable=False)
    created_at = Column(DateTime, server_default=func.now())


class KnowledgeArticleView(Base):
    """知识文章阅读记录表"""
    __tablename__ = "knowledge_article_views"

    id = Column(Integer, primary_key=True, index=True)
    article_id = Column(Integer, index=True, nullable=False)
    user_id = Column(Integer, index=True, nullable=False)
    read_duration = Column(Integer, default=0)  # 阅读时长（秒）
    created_at = Column(DateTime, server_default=func.now())
