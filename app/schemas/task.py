"""
任务协作相关 Schema
"""
from pydantic import BaseModel
from typing import Optional, List
from datetime import datetime
from app.schemas.common import CamelModel


# ============ Task 任务 ============

class TaskBase(CamelModel):
    """任务基础"""
    title: str
    description: Optional[str] = None
    priority: Optional[str] = "medium"  # low/medium/high
    status: Optional[str] = "todo"  # todo/in_progress/done/closed
    due_date: Optional[str] = None


class TaskCreate(TaskBase):
    """创建任务"""
    assignee_ids: Optional[List[int]] = None
    watcher_ids: Optional[List[int]] = None
    project_id: Optional[int] = None
    tags: Optional[List[str]] = None
    subtasks: Optional[List["SubtaskCreate"]] = None


class TaskUpdate(CamelModel):
    """更新任务"""
    title: Optional[str] = None
    description: Optional[str] = None
    priority: Optional[str] = None
    status: Optional[str] = None
    due_date: Optional[str] = None
    assignee_ids: Optional[List[int]] = None
    watcher_ids: Optional[List[int]] = None
    tags: Optional[List[str]] = None


class TaskStatusUpdate(CamelModel):
    """更新任务状态"""
    status: str  # todo/in_progress/done/closed


class TaskAssigneesUpdate(CamelModel):
    """更新任务负责人"""
    assignees: List[int]


class TaskWatchersUpdate(CamelModel):
    """更新任务关注者"""
    add: Optional[List[int]] = None
    remove: Optional[List[int]] = None


class TaskWatchUpdate(CamelModel):
    """设置关注状态"""
    watch: bool


class TaskResponse(TaskBase):
    """任务响应"""
    id: int
    assignee_ids: Optional[List[int]] = None
    assignee_names: Optional[List[str]] = None
    watcher_ids: Optional[List[int]] = None
    watcher_names: Optional[List[str]] = None
    project_id: Optional[int] = None
    tags: Optional[List[str]] = None
    parent_id: Optional[int] = None
    completed_at: Optional[datetime] = None
    created_by: Optional[int] = None
    creator_name: Optional[str] = None
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None
    subtask_count: Optional[int] = 0
    completed_subtask_count: Optional[int] = 0
    comment_count: Optional[int] = 0


class TaskListResponse(CamelModel):
    """任务列表响应"""
    items: List[TaskResponse]
    total: int
    page: int
    page_size: int


class TaskQuery(CamelModel):
    """任务查询参数"""
    status: Optional[str] = None
    priority: Optional[str] = None
    assignee_id: Optional[int] = None
    project_id: Optional[int] = None
    keyword: Optional[str] = None
    page: int = 1
    page_size: int = 20


# ============ TaskSubtask 子任务 ============

class SubtaskBase(CamelModel):
    """子任务基础"""
    title: str
    completed: Optional[bool] = False
    assignee_id: Optional[int] = None
    due_date: Optional[str] = None


class SubtaskCreate(SubtaskBase):
    """创建子任务"""
    pass


class SubtaskUpdate(CamelModel):
    """更新子任务"""
    title: Optional[str] = None
    completed: Optional[bool] = None
    assignee_id: Optional[int] = None
    due_date: Optional[str] = None


class SubtaskResponse(SubtaskBase):
    """子任务响应"""
    id: int
    task_id: int
    assignee_name: Optional[str] = None
    completed_at: Optional[datetime] = None
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None


# ============ TaskComment 任务评论 ============

class CommentBase(CamelModel):
    """评论基础"""
    content: str
    mention_users: Optional[List[int]] = None


class CommentCreate(CommentBase):
    """创建评论"""
    pass


class CommentUpdate(CamelModel):
    """更新评论"""
    content: str


class CommentResponse(CommentBase):
    """评论响应"""
    id: int
    task_id: int
    user_id: int
    user_name: Optional[str] = None
    user_avatar: Optional[str] = None
    parent_id: Optional[int] = None
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None


class CommentListResponse(CamelModel):
    """评论列表响应"""
    items: List[CommentResponse]
    total: int
    page: int
    page_size: int


# ============ TaskActivity 任务动态 ============

class ActivityResponse(CamelModel):
    """任务动态响应"""
    id: int
    task_id: int
    task_title: Optional[str] = None
    user_id: int
    user_name: Optional[str] = None
    action_type: str
    action_detail: Optional[dict] = None
    created_at: Optional[datetime] = None


class ActivityListResponse(CamelModel):
    """动态列表响应"""
    items: List[ActivityResponse]
    total: int
    page: int
    page_size: int


# ============ 批量操作 ============

class BatchStatusUpdate(CamelModel):
    """批量更新状态"""
    ids: List[int]
    status: str


class BatchDelete(CamelModel):
    """批量删除"""
    ids: List[int]


class BatchResult(CamelModel):
    """批量操作结果"""
    success: bool
    total: int
    success_count: int
    failed_count: int
    failed_items: Optional[List[dict]] = None


# ============ 任务统计 ============

class TaskStatsResponse(CamelModel):
    """任务统计响应"""
    total: int
    todo_count: int
    in_progress_count: int
    done_count: int
    closed_count: int
    overdue_count: int
    by_priority: dict
    completion_rate: float


class KanbanStatsResponse(CamelModel):
    """看板统计响应"""
    columns: List[dict]
    total: int


class UserTaskStatsResponse(CamelModel):
    """用户任务统计"""
    user_id: int
    user_name: Optional[str] = None
    total_tasks: int
    todo_count: int
    in_progress_count: int
    done_count: int
    overdue_count: int
    completion_rate: float
