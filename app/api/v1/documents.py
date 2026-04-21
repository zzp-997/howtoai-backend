"""
文档 API
"""
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from typing import List
from app.core.database import get_db
from app.schemas import (
    DocumentCategoryCreate, DocumentCategoryResponse,
    DocumentCreate, DocumentResponse, ResponseModel
)
from app.services import document_service, document_category_service
from app.api.v1.auth import get_current_user
from app.schemas.user import UserResponse

router = APIRouter(prefix="/documents", tags=["文档管理"])


# ==================== 文档分类 ====================

@router.get("/categories", response_model=ResponseModel[List[DocumentCategoryResponse]])
async def get_document_categories(
    db: AsyncSession = Depends(get_db),
    current_user: UserResponse = Depends(get_current_user)
):
    """获取文档分类列表"""
    categories = await document_category_service.find_all_ordered(db)
    return ResponseModel(data=categories)


@router.post("/categories", response_model=ResponseModel[DocumentCategoryResponse])
async def create_document_category(
    data: DocumentCategoryCreate,
    db: AsyncSession = Depends(get_db),
    current_user: UserResponse = Depends(get_current_user)
):
    """创建文档分类（管理员）"""
    if current_user.role != "admin":
        raise HTTPException(status_code=403, detail="无权限")
    category = await document_category_service.create(db, data.model_dump(by_alias=False))
    return ResponseModel(data=category)


# ==================== 文档 ====================

@router.get("", response_model=ResponseModel[List[DocumentResponse]])
async def get_documents(
    category_id: int = None,
    keyword: str = None,
    db: AsyncSession = Depends(get_db),
    current_user: UserResponse = Depends(get_current_user)
):
    """获取文档列表"""
    if keyword:
        documents = await document_service.search(db, keyword)
    elif category_id:
        documents = await document_service.find_by_category(db, category_id)
    else:
        documents = await document_service.get_all(db)
    return ResponseModel(data=documents)


@router.get("/{document_id}", response_model=ResponseModel[DocumentResponse])
async def get_document(
    document_id: int,
    db: AsyncSession = Depends(get_db),
    current_user: UserResponse = Depends(get_current_user)
):
    """获取文档详情"""
    document = await document_service.get_by_id(db, document_id)
    if not document:
        raise HTTPException(status_code=404, detail="文档不存在")
    return ResponseModel(data=document)


@router.post("", response_model=ResponseModel[DocumentResponse])
async def create_document(
    data: DocumentCreate,
    db: AsyncSession = Depends(get_db),
    current_user: UserResponse = Depends(get_current_user)
):
    """上传文档"""
    import json
    document = await document_service.create(db, {
        **data.model_dump(by_alias=False),
        "upload_by": current_user.id,
        "tags": json.dumps(data.tags) if data.tags else None
    })
    return ResponseModel(data=document)


@router.delete("/{document_id}")
async def delete_document(
    document_id: int,
    db: AsyncSession = Depends(get_db),
    current_user: UserResponse = Depends(get_current_user)
):
    """删除文档"""
    document = await document_service.get_by_id(db, document_id)
    if not document:
        raise HTTPException(status_code=404, detail="文档不存在")
    if document.upload_by != current_user.id and current_user.role != "admin":
        raise HTTPException(status_code=403, detail="无权限")

    await document_service.delete(db, document_id)
    return ResponseModel(message="删除成功")
