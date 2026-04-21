"""
待办事项 API
"""
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from typing import List
from app.core.database import get_db
from app.schemas import TodoCreate, TodoUpdate, TodoResponse, ResponseModel
from app.services import todo_service
from app.api.v1.auth import get_current_user
from app.schemas.user import UserResponse

router = APIRouter(prefix="/todos", tags=["待办事项"])


@router.get("", response_model=ResponseModel[List[TodoResponse]])
async def get_todos(
    status: str = None,
    db: AsyncSession = Depends(get_db),
    current_user: UserResponse = Depends(get_current_user)
):
    """获取待办事项列表"""
    if status == "pending":
        todos = await todo_service.find_pending(db, current_user.id)
    elif status == "completed":
        todos = await todo_service.find_completed(db, current_user.id)
    else:
        todos = await todo_service.find_by_user(db, current_user.id)
    return ResponseModel(data=todos)


@router.get("/upcoming", response_model=ResponseModel[List[TodoResponse]])
async def get_upcoming_todos(
    db: AsyncSession = Depends(get_db),
    current_user: UserResponse = Depends(get_current_user)
):
    """获取即将到期的待办"""
    todos = await todo_service.find_upcoming(db, current_user.id)
    return ResponseModel(data=todos)


@router.get("/count")
async def get_pending_count(
    db: AsyncSession = Depends(get_db),
    current_user: UserResponse = Depends(get_current_user)
):
    """获取未完成待办数量"""
    count = await todo_service.count_pending(db, current_user.id)
    return ResponseModel(data={"count": count})


@router.get("/{todo_id}", response_model=ResponseModel[TodoResponse])
async def get_todo(
    todo_id: int,
    db: AsyncSession = Depends(get_db),
    current_user: UserResponse = Depends(get_current_user)
):
    """获取待办详情"""
    todo = await todo_service.get_by_id(db, todo_id)
    if not todo or todo.user_id != current_user.id:
        raise HTTPException(status_code=404, detail="待办不存在")
    return ResponseModel(data=todo)


@router.post("", response_model=ResponseModel[TodoResponse])
async def create_todo(
    data: TodoCreate,
    db: AsyncSession = Depends(get_db),
    current_user: UserResponse = Depends(get_current_user)
):
    """创建待办"""
    todo = await todo_service.create(db, {**data.model_dump(by_alias=False), "user_id": current_user.id})
    return ResponseModel(data=todo)


@router.put("/{todo_id}", response_model=ResponseModel[TodoResponse])
async def update_todo(
    todo_id: int,
    data: TodoUpdate,
    db: AsyncSession = Depends(get_db),
    current_user: UserResponse = Depends(get_current_user)
):
    """更新待办"""
    todo = await todo_service.get_by_id(db, todo_id)
    if not todo or todo.user_id != current_user.id:
        raise HTTPException(status_code=404, detail="待办不存在")

    updated = await todo_service.update(db, todo_id, data.model_dump(exclude_unset=True, by_alias=False))
    return ResponseModel(data=updated)


@router.post("/{todo_id}/toggle", response_model=ResponseModel[TodoResponse])
async def toggle_todo(
    todo_id: int,
    db: AsyncSession = Depends(get_db),
    current_user: UserResponse = Depends(get_current_user)
):
    """切换待办完成状态"""
    todo = await todo_service.get_by_id(db, todo_id)
    if not todo or todo.user_id != current_user.id:
        raise HTTPException(status_code=404, detail="待办不存在")

    updated = await todo_service.toggle_complete(db, todo_id)
    return ResponseModel(data=updated)


@router.delete("/{todo_id}")
async def delete_todo(
    todo_id: int,
    db: AsyncSession = Depends(get_db),
    current_user: UserResponse = Depends(get_current_user)
):
    """删除待办"""
    todo = await todo_service.get_by_id(db, todo_id)
    if not todo or todo.user_id != current_user.id:
        raise HTTPException(status_code=404, detail="待办不存在")

    await todo_service.delete(db, todo_id)
    return ResponseModel(message="删除成功")
