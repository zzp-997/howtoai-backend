"""
文档服务
"""
from typing import List, Optional
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from app.models import Document, DocumentCategory
from app.services.base import BaseService


class DocumentService(BaseService[Document]):
    """文档服务"""

    def __init__(self):
        super().__init__(Document)

    async def find_by_category(self, db: AsyncSession, category_id: int) -> List[Document]:
        """按分类查询"""
        result = await db.execute(
            select(Document).where(Document.category_id == category_id).order_by(Document.created_at.desc())
        )
        return result.scalars().all()

    async def find_by_uploader(self, db: AsyncSession, user_id: int) -> List[Document]:
        """按上传者查询"""
        result = await db.execute(
            select(Document).where(Document.upload_by == user_id).order_by(Document.created_at.desc())
        )
        return result.scalars().all()

    async def search(self, db: AsyncSession, keyword: str) -> List[Document]:
        """搜索文档"""
        result = await db.execute(
            select(Document).where(Document.name.ilike(f"%{keyword}%")).order_by(Document.created_at.desc())
        )
        return result.scalars().all()


class DocumentCategoryService(BaseService[DocumentCategory]):
    """文档分类服务"""

    def __init__(self):
        super().__init__(DocumentCategory)

    async def find_all_ordered(self, db: AsyncSession) -> List[DocumentCategory]:
        """获取所有分类（按名称排序）"""
        result = await db.execute(
            select(DocumentCategory).order_by(DocumentCategory.name)
        )
        return result.scalars().all()


document_service = DocumentService()
document_category_service = DocumentCategoryService()
