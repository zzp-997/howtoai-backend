"""
知识库服务
"""
from typing import Optional, Dict, Any, List
from datetime import datetime
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func, and_, or_, text
from sqlalchemy.orm import selectinload
import json

from app.models.knowledge import (
    KnowledgeCategory, KnowledgeArticle,
    KnowledgeArticleLike, KnowledgeArticleView
)
from app.models import User


class KnowledgeService:
    """知识库服务"""

    # ========== 分类管理 ==========

    async def create_category(
        self,
        db: AsyncSession,
        category_data: Dict[str, Any],
        user_id: int
    ) -> KnowledgeCategory:
        """创建知识分类"""
        category = KnowledgeCategory(
            name=category_data["name"],
            parent_id=category_data.get("parent_id"),
            level=1,
            sort_order=category_data.get("sort_order", 0),
            created_by=user_id
        )

        # 如果有父分类，计算层级
        if category_data.get("parent_id"):
            parent = await self.get_category_by_id(db, category_data["parent_id"])
            if parent:
                category.level = parent.level + 1

        db.add(category)
        await db.commit()
        await db.refresh(category)
        return category

    async def update_category(
        self,
        db: AsyncSession,
        category_id: int,
        category_data: Dict[str, Any]
    ) -> Optional[KnowledgeCategory]:
        """更新知识分类"""
        category = await self.get_category_by_id(db, category_id)
        if not category:
            return None

        for key, value in category_data.items():
            if value is not None and hasattr(category, key):
                setattr(category, key, value)

        await db.commit()
        await db.refresh(category)
        return category

    async def delete_category(
        self,
        db: AsyncSession,
        category_id: int
    ) -> bool:
        """删除知识分类"""
        category = await self.get_category_by_id(db, category_id)
        if not category:
            return False

        # 检查是否有子分类
        children_result = await db.execute(
            select(KnowledgeCategory).where(
                KnowledgeCategory.parent_id == category_id
            ).limit(1)
        )
        if children_result.scalar_one_or_none():
            raise ValueError("该分类存在子分类，无法删除")

        # 检查是否有文章
        articles_result = await db.execute(
            select(KnowledgeArticle).where(
                KnowledgeArticle.category_id == category_id
            ).limit(1)
        )
        if articles_result.scalar_one_or_none():
            raise ValueError("该分类下存在文章，无法删除")

        await db.delete(category)
        await db.commit()
        return True

    async def get_category_by_id(
        self,
        db: AsyncSession,
        category_id: int
    ) -> Optional[KnowledgeCategory]:
        """获取分类详情"""
        result = await db.execute(
            select(KnowledgeCategory).where(KnowledgeCategory.id == category_id)
        )
        return result.scalar_one_or_none()

    async def list_categories(
        self,
        db: AsyncSession,
        parent_id: Optional[int] = None
    ) -> List[KnowledgeCategory]:
        """获取分类列表"""
        if parent_id is not None:
            stmt = select(KnowledgeCategory).where(
                KnowledgeCategory.parent_id == parent_id
            ).order_by(KnowledgeCategory.sort_order)
        else:
            stmt = select(KnowledgeCategory).order_by(KnowledgeCategory.sort_order)

        result = await db.execute(stmt)
        return list(result.scalars().all())

    async def get_category_tree(
        self,
        db: AsyncSession
    ) -> List[Dict[str, Any]]:
        """获取分类树形结构"""
        # 获取所有分类
        result = await db.execute(
            select(KnowledgeCategory).order_by(KnowledgeCategory.sort_order)
        )
        categories = list(result.scalars().all())

        # 构建树形结构
        category_map = {}
        for cat in categories:
            cat_dict = {
                "id": cat.id,
                "name": cat.name,
                "parentId": cat.parent_id,
                "level": cat.level,
                "sortOrder": cat.sort_order,
                "children": []
            }
            category_map[cat.id] = cat_dict

        root_categories = []
        for cat in categories:
            cat_dict = category_map[cat.id]
            if cat.parent_id and cat.parent_id in category_map:
                category_map[cat.parent_id]["children"].append(cat_dict)
            else:
                root_categories.append(cat_dict)

        return root_categories

    # ========== 文章管理 ==========

    async def create_article(
        self,
        db: AsyncSession,
        article_data: Dict[str, Any],
        user_id: int
    ) -> KnowledgeArticle:
        """创建知识文章"""
        article = KnowledgeArticle(
            title=article_data["title"],
            summary=article_data.get("summary"),
            content=article_data.get("content"),
            category_id=article_data.get("category_id"),
            author_id=user_id,
            tags=json.dumps(article_data.get("tags", [])) if article_data.get("tags") else None,
            status=article_data.get("status", "draft"),
            published_at=datetime.utcnow() if article_data.get("status") == "published" else None
        )

        db.add(article)
        await db.commit()
        await db.refresh(article)
        return article

    async def update_article(
        self,
        db: AsyncSession,
        article_id: int,
        article_data: Dict[str, Any]
    ) -> Optional[KnowledgeArticle]:
        """更新知识文章"""
        article = await self.get_article_by_id(db, article_id)
        if not article:
            return None

        for key, value in article_data.items():
            if value is not None:
                if key == "tags":
                    setattr(article, key, json.dumps(value) if isinstance(value, list) else value)
                elif key == "published_at" and value and article.status != "published":
                    article.status = "published"
                    setattr(article, key, value)
                elif hasattr(article, key):
                    setattr(article, key, value)

        await db.commit()
        await db.refresh(article)
        return article

    async def delete_article(
        self,
        db: AsyncSession,
        article_id: int
    ) -> bool:
        """删除知识文章"""
        article = await self.get_article_by_id(db, article_id)
        if not article:
            return False

        await db.delete(article)
        await db.commit()
        return True

    async def get_article_by_id(
        self,
        db: AsyncSession,
        article_id: int,
        user_id: Optional[int] = None
    ) -> Optional[Dict[str, Any]]:
        """获取文章详情"""
        result = await db.execute(
            select(KnowledgeArticle).where(KnowledgeArticle.id == article_id)
        )
        article = result.scalar_one_or_none()

        if not article:
            return None

        # 获取作者信息
        author_name = None
        if article.author_id:
            user_result = await db.execute(
                select(User).where(User.id == article.author_id)
            )
            user = user_result.scalar_one_or_none()
            if user:
                author_name = user.name

        # 获取分类名称
        category_name = None
        if article.category_id:
            cat_result = await db.execute(
                select(KnowledgeCategory).where(KnowledgeCategory.id == article.category_id)
            )
            cat = cat_result.scalar_one_or_none()
            if cat:
                category_name = cat.name

        # 检查是否已点赞
        is_liked = False
        if user_id:
            like_result = await db.execute(
                select(KnowledgeArticleLike).where(
                    and_(
                        KnowledgeArticleLike.article_id == article_id,
                        KnowledgeArticleLike.user_id == user_id
                    )
                )
            )
            is_liked = like_result.scalar_one_or_none() is not None

        return {
            "id": article.id,
            "title": article.title,
            "summary": article.summary,
            "content": article.content,
            "categoryId": article.category_id,
            "categoryName": category_name,
            "authorId": article.author_id,
            "authorName": author_name,
            "tags": json.loads(article.tags) if article.tags else [],
            "viewCount": article.view_count,
            "likeCount": article.like_count,
            "isLiked": is_liked,
            "status": article.status,
            "publishedAt": article.published_at,
            "createdAt": article.created_at,
            "updatedAt": article.updated_at
        }

    async def list_articles(
        self,
        db: AsyncSession,
        category_id: Optional[int] = None,
        status: Optional[str] = None,
        author_id: Optional[int] = None,
        keyword: Optional[str] = None,
        page: int = 1,
        page_size: int = 20,
        user_id: Optional[int] = None
    ) -> tuple[List[Dict[str, Any]], int]:
        """获取文章列表"""
        conditions = []
        if category_id:
            conditions.append(KnowledgeArticle.category_id == category_id)
        if status:
            conditions.append(KnowledgeArticle.status == status)
        if author_id:
            conditions.append(KnowledgeArticle.author_id == author_id)
        if keyword:
            conditions.append(
                or_(
                    KnowledgeArticle.title.like(f"%{keyword}%"),
                    KnowledgeArticle.summary.like(f"%{keyword}%")
                )
            )

        # 统计总数
        count_query = select(func.count(KnowledgeArticle.id))
        if conditions:
            count_query = count_query.where(and_(*conditions))
        count_result = await db.execute(count_query)
        total = count_result.scalar() or 0

        # 分页查询
        offset = (page - 1) * page_size
        query = select(KnowledgeArticle).order_by(KnowledgeArticle.created_at.desc())
        if conditions:
            query = query.where(and_(*conditions))
        query = query.offset(offset).limit(page_size)

        result = await db.execute(query)
        articles = result.scalars().all()

        # 转换数据
        items = []
        for article in articles:
            # 获取作者信息
            author_name = None
            if article.author_id:
                user_result = await db.execute(
                    select(User).where(User.id == article.author_id)
                )
                user = user_result.scalar_one_or_none()
                if user:
                    author_name = user.name

            # 获取分类名称
            category_name = None
            if article.category_id:
                cat_result = await db.execute(
                    select(KnowledgeCategory).where(KnowledgeCategory.id == article.category_id)
                )
                cat = cat_result.scalar_one_or_none()
                if cat:
                    category_name = cat.name

            # 检查是否已点赞
            is_liked = False
            if user_id:
                like_result = await db.execute(
                    select(KnowledgeArticleLike).where(
                        and_(
                            KnowledgeArticleLike.article_id == article.id,
                            KnowledgeArticleLike.user_id == user_id
                        )
                    )
                )
                is_liked = like_result.scalar_one_or_none() is not None

            items.append({
                "id": article.id,
                "title": article.title,
                "summary": article.summary,
                "categoryId": article.category_id,
                "categoryName": category_name,
                "authorId": article.author_id,
                "authorName": author_name,
                "tags": json.loads(article.tags) if article.tags else [],
                "viewCount": article.view_count,
                "likeCount": article.like_count,
                "isLiked": is_liked,
                "status": article.status,
                "publishedAt": article.published_at,
                "createdAt": article.created_at,
                "updatedAt": article.updated_at
            })

        return items, total

    async def search_articles(
        self,
        db: AsyncSession,
        keyword: str,
        category_id: Optional[int] = None,
        tags: Optional[List[str]] = None,
        page: int = 1,
        page_size: int = 20
    ) -> tuple[List[Dict[str, Any]], int]:
        """搜索知识库文章"""
        conditions = [
            KnowledgeArticle.status == "published",
            or_(
                KnowledgeArticle.title.like(f"%{keyword}%"),
                KnowledgeArticle.summary.like(f"%{keyword}%"),
                KnowledgeArticle.content.like(f"%{keyword}%")
            )
        ]

        if category_id:
            conditions.append(KnowledgeArticle.category_id == category_id)

        # 统计总数
        count_query = select(func.count(KnowledgeArticle.id))
        count_query = count_query.where(and_(*conditions))
        count_result = await db.execute(count_query)
        total = count_result.scalar() or 0

        # 分页查询
        offset = (page - 1) * page_size
        query = select(KnowledgeArticle).where(and_(*conditions))
        query = query.order_by(KnowledgeArticle.view_count.desc())
        query = query.offset(offset).limit(page_size)

        result = await db.execute(query)
        articles = result.scalars().all()

        # 转换数据
        items = []
        for article in articles:
            # 获取分类名称
            category_name = None
            if article.category_id:
                cat_result = await db.execute(
                    select(KnowledgeCategory).where(KnowledgeCategory.id == article.category_id)
                )
                cat = cat_result.scalar_one_or_none()
                if cat:
                    category_name = cat.name

            # 获取作者名称
            author_name = None
            if article.author_id:
                user_result = await db.execute(
                    select(User).where(User.id == article.author_id)
                )
                user = user_result.scalar_one_or_none()
                if user:
                    author_name = user.name

            # 生成高亮片段
            highlight = None
            if keyword in (article.summary or ""):
                highlight = article.summary.replace(
                    keyword, f"<em>{keyword}</em>"
                )
            elif keyword in (article.title or ""):
                highlight = article.title.replace(
                    keyword, f"<em>{keyword}</em>"
                )

            items.append({
                "id": article.id,
                "title": article.title,
                "summary": article.summary,
                "categoryName": category_name,
                "authorName": author_name,
                "viewCount": article.view_count,
                "publishedAt": article.published_at,
                "highlight": highlight
            })

        return items, total

    # ========== 点赞功能 ==========

    async def toggle_like(
        self,
        db: AsyncSession,
        article_id: int,
        user_id: int
    ) -> Dict[str, Any]:
        """切换点赞状态"""
        article = await self.get_article_by_id(db, article_id)
        if not article:
            raise ValueError("文章不存在")

        # 检查是否已点赞
        result = await db.execute(
            select(KnowledgeArticleLike).where(
                and_(
                    KnowledgeArticleLike.article_id == article_id,
                    KnowledgeArticleLike.user_id == user_id
                )
            )
        )
        existing = result.scalar_one_or_none()

        if existing:
            # 取消点赞
            await db.delete(existing)
            article["likeCount"] = max(0, article["likeCount"] - 1)
            is_liked = False
        else:
            # 添加点赞
            like = KnowledgeArticleLike(
                article_id=article_id,
                user_id=user_id
            )
            db.add(like)
            article["likeCount"] += 1
            is_liked = True

        # 更新文章点赞数
        article_result = await db.execute(
            select(KnowledgeArticle).where(KnowledgeArticle.id == article_id)
        )
        db_article = article_result.scalar_one_or_none()
        if db_article:
            db_article.like_count = article["likeCount"]

        await db.commit()

        return {
            "articleId": article_id,
            "isLiked": is_liked,
            "likeCount": article["likeCount"]
        }

    # ========== 阅读记录 ==========

    async def record_view(
        self,
        db: AsyncSession,
        article_id: int,
        user_id: int,
        read_duration: int = 0
    ) -> Dict[str, Any]:
        """记录阅读"""
        article = await self.get_article_by_id(db, article_id)
        if not article:
            raise ValueError("文章不存在")

        # 检查是否已阅读
        result = await db.execute(
            select(KnowledgeArticleView).where(
                and_(
                    KnowledgeArticleView.article_id == article_id,
                    KnowledgeArticleView.user_id == user_id
                )
            )
        )
        existing = result.scalar_one_or_none()

        is_viewed = True
        if not existing:
            # 添加阅读记录
            view = KnowledgeArticleView(
                article_id=article_id,
                user_id=user_id,
                read_duration=read_duration
            )
            db.add(view)
            is_viewed = False

            # 更新阅读数
            article_result = await db.execute(
                select(KnowledgeArticle).where(KnowledgeArticle.id == article_id)
            )
            db_article = article_result.scalar_one_or_none()
            if db_article:
                db_article.view_count += 1

            await db.commit()

        return {
            "articleId": article_id,
            "viewCount": article["viewCount"] + (0 if is_viewed else 1),
            "isViewed": is_viewed
        }


# 全局服务实例
knowledge_service = KnowledgeService()
