"""
知识库 API
"""
from fastapi import APIRouter, Depends, Query, Path
from sqlalchemy.ext.asyncio import AsyncSession
from typing import Optional, List
from app.core.database import get_db
from app.schemas.common import ResponseModel, PageResponse
from app.schemas.knowledge import (
    KnowledgeCategoryCreate, KnowledgeCategoryUpdate, KnowledgeCategoryResponse,
    KnowledgeArticleCreate, KnowledgeArticleUpdate, KnowledgeArticleResponse,
    KnowledgeArticleListResponse, KnowledgeSearchResult
)
from app.services.knowledge_service import knowledge_service
from app.api.v1.auth import get_current_user
from app.schemas.user import UserResponse

router = APIRouter(prefix="/knowledge", tags=["知识库"])


# ========== 分类管理 ==========

@router.get("/categories", response_model=ResponseModel[List[KnowledgeCategoryResponse]])
async def list_categories(
    parentId: Optional[int] = Query(None, description="父分类ID"),
    db: AsyncSession = Depends(get_db),
    current_user: UserResponse = Depends(get_current_user)
):
    """获取知识分类列表"""
    if parentId is not None:
        categories = await knowledge_service.list_categories(db, parent_id=parentId)
    else:
        # 返回树形结构
        categories = await knowledge_service.get_category_tree(db)
    return ResponseModel(code=200, message="success", data=categories)


@router.post("/categories", response_model=ResponseModel[KnowledgeCategoryResponse])
async def create_category(
    category_data: KnowledgeCategoryCreate,
    db: AsyncSession = Depends(get_db),
    current_user: UserResponse = Depends(get_current_user)
):
    """创建知识分类"""
    category = await knowledge_service.create_category(
        db, category_data.model_dump(), current_user.id
    )
    return ResponseModel(code=200, message="创建成功", data=category)


@router.put("/categories/{id}", response_model=ResponseModel[KnowledgeCategoryResponse])
async def update_category(
    id: int = Path(..., description="分类ID"),
    category_data: KnowledgeCategoryUpdate = None,
    db: AsyncSession = Depends(get_db),
    current_user: UserResponse = Depends(get_current_user)
):
    """更新知识分类"""
    category = await knowledge_service.update_category(
        db, id, category_data.model_dump(exclude_unset=True) if category_data else {}
    )
    if not category:
        return ResponseModel(code=404, message="分类不存在", data=None)
    return ResponseModel(code=200, message="更新成功", data=category)


@router.delete("/categories/{id}", response_model=ResponseModel)
async def delete_category(
    id: int = Path(..., description="分类ID"),
    db: AsyncSession = Depends(get_db),
    current_user: UserResponse = Depends(get_current_user)
):
    """删除知识分类"""
    try:
        success = await knowledge_service.delete_category(db, id)
        if not success:
            return ResponseModel(code=404, message="分类不存在", data=None)
        return ResponseModel(code=200, message="删除成功", data=None)
    except ValueError as e:
        return ResponseModel(code=400, message=str(e), data=None)


# ========== 文章管理 ==========

@router.get("/articles", response_model=ResponseModel[KnowledgeArticleListResponse])
async def list_articles(
    categoryId: Optional[int] = Query(None, description="分类ID"),
    status: Optional[str] = Query(None, description="状态"),
    authorId: Optional[int] = Query(None, description="作者ID"),
    keyword: Optional[str] = Query(None, description="搜索关键词"),
    page: int = Query(1, ge=1, description="页码"),
    pageSize: int = Query(20, ge=1, le=100, description="每页数量"),
    db: AsyncSession = Depends(get_db),
    current_user: UserResponse = Depends(get_current_user)
):
    """获取知识文章列表"""
    items, total = await knowledge_service.list_articles(
        db,
        category_id=categoryId,
        status=status,
        author_id=authorId,
        keyword=keyword,
        page=page,
        page_size=pageSize,
        user_id=current_user.id
    )
    return ResponseModel(
        code=200,
        message="success",
        data={
            "items": items,
            "total": total,
            "page": page,
            "pageSize": pageSize
        }
    )


@router.get("/articles/{id}", response_model=ResponseModel[KnowledgeArticleResponse])
async def get_article(
    id: int = Path(..., description="文章ID"),
    db: AsyncSession = Depends(get_db),
    current_user: UserResponse = Depends(get_current_user)
):
    """获取知识文章详情"""
    article = await knowledge_service.get_article_by_id(db, id, current_user.id)
    if not article:
        return ResponseModel(code=404, message="文章不存在", data=None)
    return ResponseModel(code=200, message="success", data=article)


@router.post("/articles", response_model=ResponseModel[KnowledgeArticleResponse])
async def create_article(
    article_data: KnowledgeArticleCreate,
    db: AsyncSession = Depends(get_db),
    current_user: UserResponse = Depends(get_current_user)
):
    """创建知识文章"""
    article = await knowledge_service.create_article(
        db, article_data.model_dump(), current_user.id
    )
    result = await knowledge_service.get_article_by_id(db, article.id, current_user.id)
    return ResponseModel(code=200, message="创建成功", data=result)


@router.put("/articles/{id}", response_model=ResponseModel[KnowledgeArticleResponse])
async def update_article(
    id: int = Path(..., description="文章ID"),
    article_data: KnowledgeArticleUpdate = None,
    db: AsyncSession = Depends(get_db),
    current_user: UserResponse = Depends(get_current_user)
):
    """更新知识文章"""
    article = await knowledge_service.update_article(
        db, id, article_data.model_dump(exclude_unset=True) if article_data else {}
    )
    if not article:
        return ResponseModel(code=404, message="文章不存在", data=None)
    result = await knowledge_service.get_article_by_id(db, id, current_user.id)
    return ResponseModel(code=200, message="更新成功", data=result)


@router.delete("/articles/{id}", response_model=ResponseModel)
async def delete_article(
    id: int = Path(..., description="文章ID"),
    db: AsyncSession = Depends(get_db),
    current_user: UserResponse = Depends(get_current_user)
):
    """删除知识文章"""
    success = await knowledge_service.delete_article(db, id)
    if not success:
        return ResponseModel(code=404, message="文章不存在", data=None)
    return ResponseModel(code=200, message="删除成功", data=None)


# ========== 搜索 ==========

@router.get("/search", response_model=ResponseModel)
async def search_knowledge(
    keyword: str = Query(..., description="搜索关键词"),
    categoryId: Optional[int] = Query(None, description="分类ID"),
    page: int = Query(1, ge=1, description="页码"),
    pageSize: int = Query(20, ge=1, le=100, description="每页数量"),
    db: AsyncSession = Depends(get_db),
    current_user: UserResponse = Depends(get_current_user)
):
    """搜索知识库"""
    items, total = await knowledge_service.search_articles(
        db,
        keyword=keyword,
        category_id=categoryId,
        page=page,
        page_size=pageSize
    )
    return ResponseModel(
        code=200,
        message="success",
        data={
            "items": items,
            "total": total,
            "page": page,
            "pageSize": pageSize
        }
    )


# ========== 点赞/阅读 ==========

@router.post("/articles/{id}/like", response_model=ResponseModel)
async def like_article(
    id: int = Path(..., description="文章ID"),
    db: AsyncSession = Depends(get_db),
    current_user: UserResponse = Depends(get_current_user)
):
    """点赞/取消点赞"""
    try:
        result = await knowledge_service.toggle_like(db, id, current_user.id)
        return ResponseModel(code=200, message="success", data=result)
    except ValueError as e:
        return ResponseModel(code=400, message=str(e), data=None)


@router.post("/articles/{id}/view", response_model=ResponseModel)
async def view_article(
    id: int = Path(..., description="文章ID"),
    readDuration: int = Query(0, description="阅读时长(秒)"),
    db: AsyncSession = Depends(get_db),
    current_user: UserResponse = Depends(get_current_user)
):
    """记录阅读"""
    try:
        result = await knowledge_service.record_view(db, id, current_user.id, readDuration)
        return ResponseModel(code=200, message="success", data=result)
    except ValueError as e:
        return ResponseModel(code=400, message=str(e), data=None)


# ========== 我的文章 ==========

@router.get("/my-articles", response_model=ResponseModel[KnowledgeArticleListResponse])
async def get_my_articles(
    page: int = Query(1, ge=1, description="页码"),
    pageSize: int = Query(20, ge=1, le=100, description="每页数量"),
    db: AsyncSession = Depends(get_db),
    current_user: UserResponse = Depends(get_current_user)
):
    """获取我的知识文章"""
    items, total = await knowledge_service.list_articles(
        db,
        author_id=current_user.id,
        page=page,
        page_size=pageSize,
        user_id=current_user.id
    )
    return ResponseModel(
        code=200,
        message="success",
        data={
            "items": items,
            "total": total,
            "page": page,
            "pageSize": pageSize
        }
    )
