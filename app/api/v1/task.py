"""
任务协作 API
"""
from fastapi import APIRouter, Depends, Query, Path
from sqlalchemy.ext.asyncio import AsyncSession
from typing import Optional, List
from app.core.database import get_db
from app.schemas.common import ResponseModel
from app.schemas.task import (
    TaskCreate, TaskUpdate, TaskStatusUpdate, TaskAssigneesUpdate,
    TaskWatchersUpdate, TaskWatchUpdate, TaskResponse, TaskListResponse,
    SubtaskCreate, SubtaskUpdate, SubtaskResponse,
    CommentCreate, CommentUpdate, CommentResponse, CommentListResponse,
    ActivityResponse, ActivityListResponse,
    BatchStatusUpdate, BatchDelete, BatchResult,
    TaskStatsResponse, KanbanStatsResponse, UserTaskStatsResponse
)
from app.services.task_service import task_service
from app.api.v1.auth import get_current_user
from app.schemas.user import UserResponse

router = APIRouter(prefix="/tasks", tags=["任务协作"])


# ========== 任务 CRUD ==========

@router.get("", response_model=ResponseModel[TaskListResponse])
async def list_tasks(
    status: Optional[str] = Query(None, description="任务状态"),
    priority: Optional[str] = Query(None, description="优先级"),
    assigneeId: Optional[int] = Query(None, description="负责人ID"),
    projectId: Optional[int] = Query(None, description="项目ID"),
    keyword: Optional[str] = Query(None, description="搜索关键词"),
    page: int = Query(1, ge=1, description="页码"),
    pageSize: int = Query(20, ge=1, le=100, description="每页数量"),
    db: AsyncSession = Depends(get_db),
    current_user: UserResponse = Depends(get_current_user)
):
    """获取任务列表"""
    items, total = await task_service.list_tasks(
        db,
        status=status,
        priority=priority,
        assignee_id=assigneeId,
        project_id=projectId,
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


@router.get("/{id}", response_model=ResponseModel[TaskResponse])
async def get_task(
    id: int = Path(..., description="任务ID"),
    db: AsyncSession = Depends(get_db),
    current_user: UserResponse = Depends(get_current_user)
):
    """获取任务详情"""
    task = await task_service.get_task_by_id(db, id, current_user.id)
    if not task:
        return ResponseModel(code=404, message="任务不存在", data=None)
    return ResponseModel(code=200, message="success", data=task)


@router.post("", response_model=ResponseModel[TaskResponse])
async def create_task(
    task_data: TaskCreate,
    db: AsyncSession = Depends(get_db),
    current_user: UserResponse = Depends(get_current_user)
):
    """创建任务"""
    task = await task_service.create_task(
        db, task_data.model_dump(), current_user.id
    )
    return ResponseModel(code=200, message="创建成功", data=task)


@router.put("/{id}", response_model=ResponseModel[TaskResponse])
async def update_task(
    id: int = Path(..., description="任务ID"),
    task_data: TaskUpdate = None,
    db: AsyncSession = Depends(get_db),
    current_user: UserResponse = Depends(get_current_user)
):
    """更新任务"""
    task = await task_service.update_task(
        db, id, task_data.model_dump(exclude_unset=True) if task_data else {}, current_user.id
    )
    if not task:
        return ResponseModel(code=404, message="任务不存在", data=None)
    return ResponseModel(code=200, message="更新成功", data=task)


@router.delete("/{id}", response_model=ResponseModel)
async def delete_task(
    id: int = Path(..., description="任务ID"),
    db: AsyncSession = Depends(get_db),
    current_user: UserResponse = Depends(get_current_user)
):
    """删除任务"""
    success = await task_service.delete_task(db, id, current_user.id)
    if not success:
        return ResponseModel(code=404, message="任务不存在", data=None)
    return ResponseModel(code=200, message="删除成功", data=None)


# ========== 状态更新 ==========

@router.patch("/{id}/status", response_model=ResponseModel[TaskResponse])
async def update_task_status(
    id: int = Path(..., description="任务ID"),
    status_data: TaskStatusUpdate = None,
    db: AsyncSession = Depends(get_db),
    current_user: UserResponse = Depends(get_current_user)
):
    """更新任务状态"""
    task = await task_service.update_status(
        db, id, status_data.status if status_data else "todo", current_user.id
    )
    if not task:
        return ResponseModel(code=404, message="任务不存在", data=None)
    return ResponseModel(code=200, message="更新成功", data=task)


@router.post("/batch/status", response_model=ResponseModel[BatchResult])
async def batch_update_status(
    batch_data: BatchStatusUpdate,
    db: AsyncSession = Depends(get_db),
    current_user: UserResponse = Depends(get_current_user)
):
    """批量更新任务状态"""
    result = await task_service.batch_update_status(
        db, batch_data.ids, batch_data.status, current_user.id
    )
    return ResponseModel(code=200, message="批量更新完成", data=result)


@router.post("/batch/delete", response_model=ResponseModel[BatchResult])
async def batch_delete_tasks(
    batch_data: BatchDelete,
    db: AsyncSession = Depends(get_db),
    current_user: UserResponse = Depends(get_current_user)
):
    """批量删除任务"""
    result = await task_service.batch_delete(db, batch_data.ids, current_user.id)
    return ResponseModel(code=200, message="批量删除完成", data=result)


# ========== 任务分配 ==========

@router.post("/{id}/assign", response_model=ResponseModel[TaskResponse])
async def assign_task(
    id: int = Path(..., description="任务ID"),
    assign_data: TaskAssigneesUpdate = None,
    db: AsyncSession = Depends(get_db),
    current_user: UserResponse = Depends(get_current_user)
):
    """分配任务"""
    task = await task_service.assign_task(
        db, id, assign_data.assignees if assign_data else [], current_user.id
    )
    if not task:
        return ResponseModel(code=404, message="任务不存在", data=None)
    return ResponseModel(code=200, message="分配成功", data=task)


@router.patch("/{id}/watchers", response_model=ResponseModel[TaskResponse])
async def update_watchers(
    id: int = Path(..., description="任务ID"),
    watcher_data: TaskWatchersUpdate = None,
    db: AsyncSession = Depends(get_db),
    current_user: UserResponse = Depends(get_current_user)
):
    """更新任务关注者"""
    task = await task_service.update_watchers(
        db, id,
        add_ids=watcher_data.add if watcher_data else None,
        remove_ids=watcher_data.remove if watcher_data else None,
        user_id=current_user.id
    )
    if not task:
        return ResponseModel(code=404, message="任务不存在", data=None)
    return ResponseModel(code=200, message="更新成功", data=task)


@router.post("/{id}/watch", response_model=ResponseModel[TaskResponse])
async def set_task_watch(
    id: int = Path(..., description="任务ID"),
    watch_data: TaskWatchUpdate = None,
    db: AsyncSession = Depends(get_db),
    current_user: UserResponse = Depends(get_current_user)
):
    """设置关注状态"""
    task = await task_service.set_watch(
        db, id, watch_data.watch if watch_data else False, current_user.id
    )
    if not task:
        return ResponseModel(code=404, message="任务不存在", data=None)
    return ResponseModel(code=200, message="设置成功", data=task)


# ========== 子任务 ==========

@router.get("/{id}/subtasks", response_model=ResponseModel[List[SubtaskResponse]])
async def get_subtasks(
    id: int = Path(..., description="任务ID"),
    db: AsyncSession = Depends(get_db),
    current_user: UserResponse = Depends(get_current_user)
):
    """获取子任务列表"""
    subtasks = await task_service.get_subtasks(db, id)
    return ResponseModel(code=200, message="success", data=subtasks)


@router.post("/{id}/subtasks", response_model=ResponseModel[SubtaskResponse])
async def create_subtask(
    id: int = Path(..., description="任务ID"),
    subtask_data: SubtaskCreate = None,
    db: AsyncSession = Depends(get_db),
    current_user: UserResponse = Depends(get_current_user)
):
    """添加子任务"""
    subtask = await task_service.create_subtask(
        db, id, subtask_data.model_dump() if subtask_data else {}, current_user.id
    )
    return ResponseModel(code=200, message="创建成功", data=subtask)


@router.put("/{id}/subtasks/{subtaskId}", response_model=ResponseModel[SubtaskResponse])
async def update_subtask(
    id: int = Path(..., description="任务ID"),
    subtaskId: int = Path(..., description="子任务ID"),
    subtask_data: SubtaskUpdate = None,
    db: AsyncSession = Depends(get_db),
    current_user: UserResponse = Depends(get_current_user)
):
    """更新子任务"""
    subtask = await task_service.update_subtask(
        db, id, subtaskId,
        subtask_data.model_dump(exclude_unset=True) if subtask_data else {},
        current_user.id
    )
    if not subtask:
        return ResponseModel(code=404, message="子任务不存在", data=None)
    return ResponseModel(code=200, message="更新成功", data=subtask)


@router.delete("/{id}/subtasks/{subtaskId}", response_model=ResponseModel)
async def delete_subtask(
    id: int = Path(..., description="任务ID"),
    subtaskId: int = Path(..., description="子任务ID"),
    db: AsyncSession = Depends(get_db),
    current_user: UserResponse = Depends(get_current_user)
):
    """删除子任务"""
    success = await task_service.delete_subtask(db, id, subtaskId, current_user.id)
    if not success:
        return ResponseModel(code=404, message="子任务不存在", data=None)
    return ResponseModel(code=200, message="删除成功", data=None)


@router.post("/{id}/subtasks/{subtaskId}/toggle", response_model=ResponseModel[SubtaskResponse])
async def toggle_subtask(
    id: int = Path(..., description="任务ID"),
    subtaskId: int = Path(..., description="子任务ID"),
    db: AsyncSession = Depends(get_db),
    current_user: UserResponse = Depends(get_current_user)
):
    """切换子任务完成状态"""
    subtask = await task_service.toggle_subtask(db, id, subtaskId, current_user.id)
    if not subtask:
        return ResponseModel(code=404, message="子任务不存在", data=None)
    return ResponseModel(code=200, message="切换成功", data=subtask)


# ========== 评论 ==========

@router.get("/{id}/comments", response_model=ResponseModel[CommentListResponse])
async def get_comments(
    id: int = Path(..., description="任务ID"),
    page: int = Query(1, ge=1, description="页码"),
    pageSize: int = Query(20, ge=1, le=100, description="每页数量"),
    db: AsyncSession = Depends(get_db),
    current_user: UserResponse = Depends(get_current_user)
):
    """获取评论列表"""
    items, total = await task_service.get_comments(db, id, page, pageSize)
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


@router.post("/{id}/comments", response_model=ResponseModel[CommentResponse])
async def create_comment(
    id: int = Path(..., description="任务ID"),
    comment_data: CommentCreate = None,
    db: AsyncSession = Depends(get_db),
    current_user: UserResponse = Depends(get_current_user)
):
    """发表评论"""
    comment = await task_service.create_comment(
        db, id,
        content=comment_data.content if comment_data else "",
        user_id=current_user.id,
        mention_users=comment_data.mention_users if comment_data else None
    )
    return ResponseModel(code=200, message="评论成功", data=comment)


@router.put("/{id}/comments/{commentId}", response_model=ResponseModel[CommentResponse])
async def update_comment(
    id: int = Path(..., description="任务ID"),
    commentId: int = Path(..., description="评论ID"),
    comment_data: CommentUpdate = None,
    db: AsyncSession = Depends(get_db),
    current_user: UserResponse = Depends(get_current_user)
):
    """更新评论"""
    comment = await task_service.update_comment(
        db, id, commentId,
        content=comment_data.content if comment_data else "",
        user_id=current_user.id
    )
    if not comment:
        return ResponseModel(code=404, message="评论不存在", data=None)
    return ResponseModel(code=200, message="更新成功", data=comment)


@router.delete("/{id}/comments/{commentId}", response_model=ResponseModel)
async def delete_comment(
    id: int = Path(..., description="任务ID"),
    commentId: int = Path(..., description="评论ID"),
    db: AsyncSession = Depends(get_db),
    current_user: UserResponse = Depends(get_current_user)
):
    """删除评论"""
    try:
        success = await task_service.delete_comment(db, id, commentId, current_user.id)
        if not success:
            return ResponseModel(code=404, message="评论不存在", data=None)
        return ResponseModel(code=200, message="删除成功", data=None)
    except ValueError as e:
        return ResponseModel(code=400, message=str(e), data=None)


# ========== 活动动态 ==========

@router.get("/{id}/activities", response_model=ResponseModel[ActivityListResponse])
async def get_activities(
    id: int = Path(..., description="任务ID"),
    page: int = Query(1, ge=1, description="页码"),
    pageSize: int = Query(20, ge=1, le=100, description="每页数量"),
    db: AsyncSession = Depends(get_db),
    current_user: UserResponse = Depends(get_current_user)
):
    """获取任务动态"""
    items, total = await task_service.get_activities(db, id, page, pageSize)
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


@router.get("/activities/me", response_model=ResponseModel[ActivityListResponse])
async def get_my_activities(
    page: int = Query(1, ge=1, description="页码"),
    pageSize: int = Query(20, ge=1, le=100, description="每页数量"),
    db: AsyncSession = Depends(get_db),
    current_user: UserResponse = Depends(get_current_user)
):
    """获取我的任务动态"""
    items, total = await task_service.get_my_activities(db, current_user.id, page, pageSize)
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


# ========== 任务统计 ==========

@router.get("/stats", response_model=ResponseModel[TaskStatsResponse])
async def get_stats(
    db: AsyncSession = Depends(get_db),
    current_user: UserResponse = Depends(get_current_user)
):
    """获取任务统计"""
    stats = await task_service.get_stats(db)
    return ResponseModel(code=200, message="success", data=stats)


@router.get("/kanban/stats", response_model=ResponseModel[KanbanStatsResponse])
async def get_kanban_stats(
    db: AsyncSession = Depends(get_db),
    current_user: UserResponse = Depends(get_current_user)
):
    """获取看板统计"""
    stats = await task_service.get_kanban_stats(db)
    return ResponseModel(code=200, message="success", data=stats)


@router.get("/stats/user/{userId}", response_model=ResponseModel[UserTaskStatsResponse])
async def get_user_stats(
    userId: int = Path(..., description="用户ID"),
    db: AsyncSession = Depends(get_db),
    current_user: UserResponse = Depends(get_current_user)
):
    """获取用户任务统计"""
    stats = await task_service.get_user_task_stats(db, userId)
    return ResponseModel(code=200, message="success", data=stats)


# ========== 搜索 ==========

@router.get("/search", response_model=ResponseModel[TaskListResponse])
async def search_tasks(
    keyword: Optional[str] = Query(None, description="搜索关键词"),
    status: Optional[str] = Query(None, description="状态筛选"),
    priority: Optional[str] = Query(None, description="优先级筛选"),
    page: int = Query(1, ge=1, description="页码"),
    pageSize: int = Query(20, ge=1, le=100, description="每页数量"),
    db: AsyncSession = Depends(get_db),
    current_user: UserResponse = Depends(get_current_user)
):
    """搜索任务"""
    items, total = await task_service.list_tasks(
        db,
        keyword=keyword,
        status=status,
        priority=priority,
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
