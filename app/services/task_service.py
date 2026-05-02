"""
任务协作服务
"""
from typing import Optional, Dict, Any, List
from datetime import datetime
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func, and_, or_
import json

from app.models.task import (
    Task, TaskSubtask, TaskComment, TaskActivity
)
from app.models import User


class TaskService:
    """任务协作服务"""

    # ========== 任务 CRUD ==========

    async def create_task(
        self,
        db: AsyncSession,
        task_data: Dict[str, Any],
        user_id: int
    ) -> Dict[str, Any]:
        """创建任务"""
        task = Task(
            title=task_data["title"],
            description=task_data.get("description"),
            priority=task_data.get("priority", "medium"),
            status=task_data.get("status", "todo"),
            assignee_ids=json.dumps(task_data.get("assignee_ids", [])) if task_data.get("assignee_ids") else None,
            watcher_ids=json.dumps(task_data.get("watcher_ids", [])) if task_data.get("watcher_ids") else None,
            due_date=task_data.get("due_date"),
            project_id=task_data.get("project_id"),
            tags=json.dumps(task_data.get("tags", [])) if task_data.get("tags") else None,
            parent_id=task_data.get("parent_id"),
            created_by=user_id
        )

        db.add(task)
        await db.flush()

        # 如果有子任务，创建子任务
        subtasks_data = task_data.get("subtasks", [])
        for subtask_data in subtasks_data:
            subtask = TaskSubtask(
                task_id=task.id,
                title=subtask_data["title"],
                completed=False,
                assignee_id=subtask_data.get("assignee_id"),
                due_date=subtask_data.get("due_date")
            )
            db.add(subtask)

        # 记录活动
        activity = TaskActivity(
            task_id=task.id,
            user_id=user_id,
            action_type="create",
            action_detail=json.dumps({"title": task.title})
        )
        db.add(activity)

        await db.commit()
        await db.refresh(task)

        return await self.get_task_by_id(db, task.id, user_id)

    async def update_task(
        self,
        db: AsyncSession,
        task_id: int,
        task_data: Dict[str, Any],
        user_id: int
    ) -> Optional[Dict[str, Any]]:
        """更新任务"""
        task = await self.get_task_raw(db, task_id)
        if not task:
            return None

        old_values = {}
        for key, value in task_data.items():
            if value is not None and hasattr(task, key):
                old_values[key] = getattr(task, key)
                if key in ("assignee_ids", "watcher_ids", "tags"):
                    setattr(task, key, json.dumps(value) if isinstance(value, list) else value)
                else:
                    setattr(task, key, value)

        # 记录活动
        activity = TaskActivity(
            task_id=task_id,
            user_id=user_id,
            action_type="update",
            action_detail=json.dumps({"changes": list(task_data.keys())})
        )
        db.add(activity)

        await db.commit()
        await db.refresh(task)

        return await self.get_task_by_id(db, task_id, user_id)

    async def delete_task(
        self,
        db: AsyncSession,
        task_id: int,
        user_id: int
    ) -> bool:
        """删除任务"""
        task = await self.get_task_raw(db, task_id)
        if not task:
            return False

        # 记录活动
        activity = TaskActivity(
            task_id=task_id,
            user_id=user_id,
            action_type="delete",
            action_detail=json.dumps({"title": task.title})
        )
        db.add(activity)

        await db.delete(task)
        await db.commit()
        return True

    async def get_task_raw(
        self,
        db: AsyncSession,
        task_id: int
    ) -> Optional[Task]:
        """获取任务原始对象"""
        result = await db.execute(
            select(Task).where(Task.id == task_id)
        )
        return result.scalar_one_or_none()

    async def get_task_by_id(
        self,
        db: AsyncSession,
        task_id: int,
        user_id: Optional[int] = None
    ) -> Optional[Dict[str, Any]]:
        """获取任务详情"""
        task = await self.get_task_raw(db, task_id)
        if not task:
            return None

        # 获取创建者信息
        creator_name = None
        if task.created_by:
            user_result = await db.execute(
                select(User).where(User.id == task.created_by)
            )
            user = user_result.scalar_one_or_none()
            if user:
                creator_name = user.name

        # 获取负责人信息
        assignee_ids = json.loads(task.assignee_ids) if task.assignee_ids else []
        assignee_names = []
        for aid in assignee_ids:
            user_result = await db.execute(
                select(User).where(User.id == aid)
            )
            user = user_result.scalar_one_or_none()
            if user:
                assignee_names.append(user.name)

        # 获取关注者信息
        watcher_ids = json.loads(task.watcher_ids) if task.watcher_ids else []
        watcher_names = []
        for wid in watcher_ids:
            user_result = await db.execute(
                select(User).where(User.id == wid)
            )
            user = user_result.scalar_one_or_none()
            if user:
                watcher_names.append(user.name)

        # 获取子任务统计
        subtask_result = await db.execute(
            select(func.count(TaskSubtask.id)).where(TaskSubtask.task_id == task_id)
        )
        subtask_count = subtask_result.scalar() or 0

        completed_subtask_result = await db.execute(
            select(func.count(TaskSubtask.id)).where(
                and_(TaskSubtask.task_id == task_id, TaskSubtask.completed == True)
            )
        )
        completed_subtask_count = completed_subtask_result.scalar() or 0

        # 获取评论数
        comment_result = await db.execute(
            select(func.count(TaskComment.id)).where(TaskComment.task_id == task_id)
        )
        comment_count = comment_result.scalar() or 0

        return {
            "id": task.id,
            "title": task.title,
            "description": task.description,
            "priority": task.priority,
            "status": task.status,
            "assigneeIds": assignee_ids,
            "assigneeNames": assignee_names,
            "watcherIds": watcher_ids,
            "watcherNames": watcher_names,
            "dueDate": task.due_date,
            "projectId": task.project_id,
            "tags": json.loads(task.tags) if task.tags else [],
            "parentId": task.parent_id,
            "completedAt": task.completed_at,
            "createdBy": task.created_by,
            "creatorName": creator_name,
            "createdAt": task.created_at,
            "updatedAt": task.updated_at,
            "subtaskCount": subtask_count,
            "completedSubtaskCount": completed_subtask_count,
            "commentCount": comment_count
        }

    async def list_tasks(
        self,
        db: AsyncSession,
        status: Optional[str] = None,
        priority: Optional[str] = None,
        assignee_id: Optional[int] = None,
        project_id: Optional[int] = None,
        keyword: Optional[str] = None,
        page: int = 1,
        page_size: int = 20,
        user_id: Optional[int] = None
    ) -> tuple[List[Dict[str, Any]], int]:
        """获取任务列表"""
        conditions = []
        if status:
            conditions.append(Task.status == status)
        if priority:
            conditions.append(Task.priority == priority)
        if project_id:
            conditions.append(Task.project_id == project_id)
        if keyword:
            conditions.append(
                or_(
                    Task.title.like(f"%{keyword}%"),
                    Task.description.like(f"%{keyword}%")
                )
            )
        if assignee_id:
            # 模糊匹配负责人
            conditions.append(Task.assignee_ids.like(f"%{assignee_id}%"))

        # 只查询主任务（parent_id 为空）
        conditions.append(Task.parent_id == None)

        # 统计总数
        count_query = select(func.count(Task.id))
        if conditions:
            count_query = count_query.where(and_(*conditions))
        count_result = await db.execute(count_query)
        total = count_result.scalar() or 0

        # 分页查询
        offset = (page - 1) * page_size
        query = select(Task).order_by(Task.created_at.desc())
        if conditions:
            query = query.where(and_(*conditions))
        query = query.offset(offset).limit(page_size)

        result = await db.execute(query)
        tasks = result.scalars().all()

        # 转换数据
        items = []
        for task in tasks:
            items.append(await self.get_task_by_id(db, task.id, user_id))

        return items, total

    # ========== 状态更新 ==========

    async def update_status(
        self,
        db: AsyncSession,
        task_id: int,
        status: str,
        user_id: int
    ) -> Optional[Dict[str, Any]]:
        """更新任务状态"""
        task = await self.get_task_raw(db, task_id)
        if not task:
            return None

        old_status = task.status
        task.status = status

        if status == "done":
            task.completed_at = datetime.utcnow()
        elif old_status == "done":
            task.completed_at = None

        # 记录活动
        activity = TaskActivity(
            task_id=task_id,
            user_id=user_id,
            action_type="status_change",
            action_detail=json.dumps({"from": old_status, "to": status})
        )
        db.add(activity)

        await db.commit()
        await db.refresh(task)

        return await self.get_task_by_id(db, task_id, user_id)

    async def batch_update_status(
        self,
        db: AsyncSession,
        task_ids: List[int],
        status: str,
        user_id: int
    ) -> Dict[str, Any]:
        """批量更新状态"""
        success_count = 0
        failed_items = []

        for task_id in task_ids:
            try:
                await self.update_status(db, task_id, status, user_id)
                success_count += 1
            except Exception as e:
                failed_items.append({
                    "id": task_id,
                    "error": str(e)
                })

        return {
            "success": True,
            "total": len(task_ids),
            "successCount": success_count,
            "failedCount": len(failed_items),
            "failedItems": failed_items
        }

    async def batch_delete(
        self,
        db: AsyncSession,
        task_ids: List[int],
        user_id: int
    ) -> Dict[str, Any]:
        """批量删除任务"""
        success_count = 0
        failed_items = []

        for task_id in task_ids:
            try:
                success = await self.delete_task(db, task_id, user_id)
                if success:
                    success_count += 1
                else:
                    failed_items.append({
                        "id": task_id,
                        "error": "Task not found"
                    })
            except Exception as e:
                failed_items.append({
                    "id": task_id,
                    "error": str(e)
                })

        return {
            "success": True,
            "total": len(task_ids),
            "successCount": success_count,
            "failedCount": len(failed_items),
            "failedItems": failed_items
        }

    # ========== 任务分配 ==========

    async def assign_task(
        self,
        db: AsyncSession,
        task_id: int,
        assignee_ids: List[int],
        user_id: int
    ) -> Optional[Dict[str, Any]]:
        """分配任务"""
        task = await self.get_task_raw(db, task_id)
        if not task:
            return None

        old_assignees = json.loads(task.assignee_ids) if task.assignee_ids else []
        task.assignee_ids = json.dumps(assignee_ids)

        # 记录活动
        activity = TaskActivity(
            task_id=task_id,
            user_id=user_id,
            action_type="assign",
            action_detail=json.dumps({
                "from": old_assignees,
                "to": assignee_ids
            })
        )
        db.add(activity)

        await db.commit()
        await db.refresh(task)

        return await self.get_task_by_id(db, task_id, user_id)

    async def update_watchers(
        self,
        db: AsyncSession,
        task_id: int,
        add_ids: Optional[List[int]] = None,
        remove_ids: Optional[List[int]] = None,
        user_id: Optional[int] = None
    ) -> Optional[Dict[str, Any]]:
        """更新关注者"""
        task = await self.get_task_raw(db, task_id)
        if not task:
            return None

        current_watchers = set(json.loads(task.watcher_ids) if task.watcher_ids else [])

        if add_ids:
            current_watchers.update(add_ids)
        if remove_ids:
            current_watchers.difference_update(remove_ids)

        task.watcher_ids = json.dumps(list(current_watchers))

        # 记录活动
        activity = TaskActivity(
            task_id=task_id,
            user_id=user_id or 0,
            action_type="watcher",
            action_detail=json.dumps({
                "add": add_ids or [],
                "remove": remove_ids or []
            })
        )
        db.add(activity)

        await db.commit()
        await db.refresh(task)

        return await self.get_task_by_id(db, task_id, user_id)

    async def set_watch(
        self,
        db: AsyncSession,
        task_id: int,
        watch: bool,
        user_id: int
    ) -> Optional[Dict[str, Any]]:
        """设置关注状态"""
        task = await self.get_task_raw(db, task_id)
        if not task:
            return None

        current_watchers = set(json.loads(task.watcher_ids) if task.watcher_ids else [])

        if watch:
            current_watchers.add(user_id)
        else:
            current_watchers.discard(user_id)

        task.watcher_ids = json.dumps(list(current_watchers))

        # 记录活动
        activity = TaskActivity(
            task_id=task_id,
            user_id=user_id,
            action_type="watcher",
            action_detail=json.dumps({"action": "watch" if watch else "unwatch"})
        )
        db.add(activity)

        await db.commit()
        await db.refresh(task)

        return await self.get_task_by_id(db, task_id, user_id)

    # ========== 子任务 ==========

    async def get_subtasks(
        self,
        db: AsyncSession,
        task_id: int
    ) -> List[Dict[str, Any]]:
        """获取子任务列表"""
        result = await db.execute(
            select(TaskSubtask).where(TaskSubtask.task_id == task_id)
            .order_by(TaskSubtask.created_at)
        )
        subtasks = result.scalars().all()

        items = []
        for subtask in subtasks:
            assignee_name = None
            if subtask.assignee_id:
                user_result = await db.execute(
                    select(User).where(User.id == subtask.assignee_id)
                )
                user = user_result.scalar_one_or_none()
                if user:
                    assignee_name = user.name

            items.append({
                "id": subtask.id,
                "taskId": subtask.task_id,
                "title": subtask.title,
                "completed": subtask.completed,
                "assigneeId": subtask.assignee_id,
                "assigneeName": assignee_name,
                "dueDate": subtask.due_date,
                "completedAt": subtask.completed_at,
                "createdAt": subtask.created_at,
                "updatedAt": subtask.updated_at
            })

        return items

    async def create_subtask(
        self,
        db: AsyncSession,
        task_id: int,
        subtask_data: Dict[str, Any],
        user_id: int
    ) -> Dict[str, Any]:
        """创建子任务"""
        subtask = TaskSubtask(
            task_id=task_id,
            title=subtask_data["title"],
            completed=False,
            assignee_id=subtask_data.get("assignee_id"),
            due_date=subtask_data.get("due_date")
        )

        db.add(subtask)
        await db.flush()

        # 记录活动
        activity = TaskActivity(
            task_id=task_id,
            user_id=user_id,
            action_type="subtask",
            action_detail=json.dumps({"action": "create", "title": subtask_data["title"]})
        )
        db.add(activity)

        await db.commit()
        await db.refresh(subtask)

        return await self.get_subtask_by_id(db, subtask.id)

    async def update_subtask(
        self,
        db: AsyncSession,
        task_id: int,
        subtask_id: int,
        subtask_data: Dict[str, Any],
        user_id: int
    ) -> Optional[Dict[str, Any]]:
        """更新子任务"""
        result = await db.execute(
            select(TaskSubtask).where(
                and_(TaskSubtask.id == subtask_id, TaskSubtask.task_id == task_id)
            )
        )
        subtask = result.scalar_one_or_none()
        if not subtask:
            return None

        for key, value in subtask_data.items():
            if value is not None and hasattr(subtask, key):
                if key == "completed" and value:
                    subtask.completed_at = datetime.utcnow()
                elif key == "completed":
                    subtask.completed_at = None
                setattr(subtask, key, value)

        # 记录活动
        activity = TaskActivity(
            task_id=task_id,
            user_id=user_id,
            action_type="subtask",
            action_detail=json.dumps({"action": "update", "subtaskId": subtask_id})
        )
        db.add(activity)

        await db.commit()
        await db.refresh(subtask)

        return await self.get_subtask_by_id(db, subtask_id)

    async def delete_subtask(
        self,
        db: AsyncSession,
        task_id: int,
        subtask_id: int,
        user_id: int
    ) -> bool:
        """删除子任务"""
        result = await db.execute(
            select(TaskSubtask).where(
                and_(TaskSubtask.id == subtask_id, TaskSubtask.task_id == task_id)
            )
        )
        subtask = result.scalar_one_or_none()
        if not subtask:
            return False

        # 记录活动
        activity = TaskActivity(
            task_id=task_id,
            user_id=user_id,
            action_type="subtask",
            action_detail=json.dumps({"action": "delete", "title": subtask.title})
        )
        db.add(activity)

        await db.delete(subtask)
        await db.commit()
        return True

    async def toggle_subtask(
        self,
        db: AsyncSession,
        task_id: int,
        subtask_id: int,
        user_id: int
    ) -> Optional[Dict[str, Any]]:
        """切换子任务完成状态"""
        result = await db.execute(
            select(TaskSubtask).where(
                and_(TaskSubtask.id == subtask_id, TaskSubtask.task_id == task_id)
            )
        )
        subtask = result.scalar_one_or_none()
        if not subtask:
            return None

        subtask.completed = not subtask.completed
        subtask.completed_at = datetime.utcnow() if subtask.completed else None

        # 记录活动
        activity = TaskActivity(
            task_id=task_id,
            user_id=user_id,
            action_type="subtask",
            action_detail=json.dumps({
                "action": "toggle",
                "subtaskId": subtask_id,
                "completed": subtask.completed
            })
        )
        db.add(activity)

        await db.commit()
        await db.refresh(subtask)

        return await self.get_subtask_by_id(db, subtask_id)

    async def get_subtask_by_id(
        self,
        db: AsyncSession,
        subtask_id: int
    ) -> Optional[Dict[str, Any]]:
        """获取子任务详情"""
        result = await db.execute(
            select(TaskSubtask).where(TaskSubtask.id == subtask_id)
        )
        subtask = result.scalar_one_or_none()
        if not subtask:
            return None

        assignee_name = None
        if subtask.assignee_id:
            user_result = await db.execute(
                select(User).where(User.id == subtask.assignee_id)
            )
            user = user_result.scalar_one_or_none()
            if user:
                assignee_name = user.name

        return {
            "id": subtask.id,
            "taskId": subtask.task_id,
            "title": subtask.title,
            "completed": subtask.completed,
            "assigneeId": subtask.assignee_id,
            "assigneeName": assignee_name,
            "dueDate": subtask.due_date,
            "completedAt": subtask.completed_at,
            "createdAt": subtask.created_at,
            "updatedAt": subtask.updated_at
        }

    # ========== 评论 ==========

    async def get_comments(
        self,
        db: AsyncSession,
        task_id: int,
        page: int = 1,
        page_size: int = 20
    ) -> tuple[List[Dict[str, Any]], int]:
        """获取评论列表"""
        # 统计总数
        count_result = await db.execute(
            select(func.count(TaskComment.id)).where(TaskComment.task_id == task_id)
        )
        total = count_result.scalar() or 0

        # 分页查询
        offset = (page - 1) * page_size
        result = await db.execute(
            select(TaskComment).where(TaskComment.task_id == task_id)
            .order_by(TaskComment.created_at)
            .offset(offset).limit(page_size)
        )
        comments = result.scalars().all()

        items = []
        for comment in comments:
            user_name = None
            user_avatar = None
            if comment.user_id:
                user_result = await db.execute(
                    select(User).where(User.id == comment.user_id)
                )
                user = user_result.scalar_one_or_none()
                if user:
                    user_name = user.name
                    user_avatar = user.avatar

            items.append({
                "id": comment.id,
                "taskId": comment.task_id,
                "userId": comment.user_id,
                "userName": user_name,
                "userAvatar": user_avatar,
                "content": comment.content,
                "mentionUsers": json.loads(comment.mention_users) if comment.mention_users else [],
                "parentId": comment.parent_id,
                "createdAt": comment.created_at,
                "updatedAt": comment.updated_at
            })

        return items, total

    async def create_comment(
        self,
        db: AsyncSession,
        task_id: int,
        content: str,
        user_id: int,
        mention_users: Optional[List[int]] = None
    ) -> Dict[str, Any]:
        """创建评论"""
        comment = TaskComment(
            task_id=task_id,
            user_id=user_id,
            content=content,
            mention_users=json.dumps(mention_users) if mention_users else None
        )

        db.add(comment)
        await db.flush()

        # 记录活动
        activity = TaskActivity(
            task_id=task_id,
            user_id=user_id,
            action_type="comment",
            action_detail=json.dumps({"commentId": comment.id})
        )
        db.add(activity)

        await db.commit()
        await db.refresh(comment)

        return await self.get_comment_by_id(db, comment.id)

    async def update_comment(
        self,
        db: AsyncSession,
        task_id: int,
        comment_id: int,
        content: str,
        user_id: int
    ) -> Optional[Dict[str, Any]]:
        """更新评论"""
        result = await db.execute(
            select(TaskComment).where(
                and_(
                    TaskComment.id == comment_id,
                    TaskComment.task_id == task_id,
                    TaskComment.user_id == user_id
                )
            )
        )
        comment = result.scalar_one_or_none()
        if not comment:
            return None

        comment.content = content
        await db.commit()
        await db.refresh(comment)

        return await self.get_comment_by_id(db, comment_id)

    async def delete_comment(
        self,
        db: AsyncSession,
        task_id: int,
        comment_id: int,
        user_id: int
    ) -> bool:
        """删除评论"""
        result = await db.execute(
            select(TaskComment).where(
                and_(
                    TaskComment.id == comment_id,
                    TaskComment.task_id == task_id
                )
            )
        )
        comment = result.scalar_one_or_none()
        if not comment:
            return False

        # 只能删除自己的评论
        if comment.user_id != user_id:
            raise ValueError("只能删除自己的评论")

        await db.delete(comment)
        await db.commit()
        return True

    async def get_comment_by_id(
        self,
        db: AsyncSession,
        comment_id: int
    ) -> Optional[Dict[str, Any]]:
        """获取评论详情"""
        result = await db.execute(
            select(TaskComment).where(TaskComment.id == comment_id)
        )
        comment = result.scalar_one_or_none()
        if not comment:
            return None

        user_name = None
        user_avatar = None
        if comment.user_id:
            user_result = await db.execute(
                select(User).where(User.id == comment.user_id)
            )
            user = user_result.scalar_one_or_none()
            if user:
                user_name = user.name
                user_avatar = user.avatar

        return {
            "id": comment.id,
            "taskId": comment.task_id,
            "userId": comment.user_id,
            "userName": user_name,
            "userAvatar": user_avatar,
            "content": comment.content,
            "mentionUsers": json.loads(comment.mention_users) if comment.mention_users else [],
            "parentId": comment.parent_id,
            "createdAt": comment.created_at,
            "updatedAt": comment.updated_at
        }

    # ========== 活动动态 ==========

    async def get_activities(
        self,
        db: AsyncSession,
        task_id: int,
        page: int = 1,
        page_size: int = 20
    ) -> tuple[List[Dict[str, Any]], int]:
        """获取任务动态"""
        # 统计总数
        count_result = await db.execute(
            select(func.count(TaskActivity.id)).where(TaskActivity.task_id == task_id)
        )
        total = count_result.scalar() or 0

        # 分页查询
        offset = (page - 1) * page_size
        result = await db.execute(
            select(TaskActivity).where(TaskActivity.task_id == task_id)
            .order_by(TaskActivity.created_at.desc())
            .offset(offset).limit(page_size)
        )
        activities = result.scalars().all()

        items = []
        for activity in activities:
            user_name = None
            if activity.user_id:
                user_result = await db.execute(
                    select(User).where(User.id == activity.user_id)
                )
                user = user_result.scalar_one_or_none()
                if user:
                    user_name = user.name

            # 获取任务标题
            task_title = None
            task_result = await db.execute(
                select(Task).where(Task.id == activity.task_id)
            )
            task = task_result.scalar_one_or_none()
            if task:
                task_title = task.title

            items.append({
                "id": activity.id,
                "taskId": activity.task_id,
                "taskTitle": task_title,
                "userId": activity.user_id,
                "userName": user_name,
                "actionType": activity.action_type,
                "actionDetail": json.loads(activity.action_detail) if activity.action_detail else None,
                "createdAt": activity.created_at
            })

        return items, total

    async def get_my_activities(
        self,
        db: AsyncSession,
        user_id: int,
        page: int = 1,
        page_size: int = 20
    ) -> tuple[List[Dict[str, Any]], int]:
        """获取我的任务动态"""
        # 统计总数
        count_result = await db.execute(
            select(func.count(TaskActivity.id)).where(TaskActivity.user_id == user_id)
        )
        total = count_result.scalar() or 0

        # 分页查询
        offset = (page - 1) * page_size
        result = await db.execute(
            select(TaskActivity).where(TaskActivity.user_id == user_id)
            .order_by(TaskActivity.created_at.desc())
            .offset(offset).limit(page_size)
        )
        activities = result.scalars().all()

        items = []
        for activity in activities:
            # 获取任务信息
            task_title = None
            task_result = await db.execute(
                select(Task).where(Task.id == activity.task_id)
            )
            task = task_result.scalar_one_or_none()
            if task:
                task_title = task.title

            items.append({
                "id": activity.id,
                "taskId": activity.task_id,
                "taskTitle": task_title,
                "userId": activity.user_id,
                "userName": None,
                "actionType": activity.action_type,
                "actionDetail": json.loads(activity.action_detail) if activity.action_detail else None,
                "createdAt": activity.created_at
            })

        return items, total

    # ========== 统计 ==========

    async def get_stats(
        self,
        db: AsyncSession
    ) -> Dict[str, Any]:
        """获取任务统计"""
        # 统计各状态数量
        status_counts = {}
        for status in ["todo", "in_progress", "done", "closed"]:
            result = await db.execute(
                select(func.count(Task.id)).where(
                    and_(Task.status == status, Task.parent_id == None)
                )
            )
            status_counts[status] = result.scalar() or 0

        # 统计优先级
        priority_counts = {}
        for priority in ["low", "medium", "high"]:
            result = await db.execute(
                select(func.count(Task.id)).where(
                    and_(Task.priority == priority, Task.parent_id == None)
                )
            )
            priority_counts[priority] = result.scalar() or 0

        # 统计总数
        total_result = await db.execute(
            select(func.count(Task.id)).where(Task.parent_id == None)
        )
        total = total_result.scalar() or 0

        # 计算完成率
        completion_rate = (status_counts.get("done", 0) / total * 100) if total > 0 else 0

        # 统计过期任务
        today = datetime.now().strftime("%Y-%m-%d")
        overdue_result = await db.execute(
            select(func.count(Task.id)).where(
                and_(
                    Task.due_date < today,
                    Task.status.in_(["todo", "in_progress"]),
                    Task.parent_id == None
                )
            )
        )
        overdue_count = overdue_result.scalar() or 0

        return {
            "total": total,
            "todoCount": status_counts.get("todo", 0),
            "inProgressCount": status_counts.get("in_progress", 0),
            "doneCount": status_counts.get("done", 0),
            "closedCount": status_counts.get("closed", 0),
            "overdueCount": overdue_count,
            "byPriority": priority_counts,
            "completionRate": round(completion_rate, 2)
        }

    async def get_kanban_stats(
        self,
        db: AsyncSession
    ) -> Dict[str, Any]:
        """获取看板统计"""
        columns = []
        for status, label in [("todo", "待处理"), ("in_progress", "进行中"), ("done", "已完成")]:
            result = await db.execute(
                select(Task).where(
                    and_(Task.status == status, Task.parent_id == None)
                )
            )
            tasks = result.scalars().all()

            columns.append({
                "status": status,
                "label": label,
                "count": len(tasks),
                "tasks": [
                    {
                        "id": t.id,
                        "title": t.title,
                        "priority": t.priority,
                        "dueDate": t.due_date
                    }
                    for t in tasks[:10]  # 每个状态最多显示10个
                ]
            })

        total_result = await db.execute(
            select(func.count(Task.id)).where(Task.parent_id == None)
        )
        total = total_result.scalar() or 0

        return {
            "columns": columns,
            "total": total
        }

    async def get_user_task_stats(
        self,
        db: AsyncSession,
        user_id: int
    ) -> Dict[str, Any]:
        """获取用户任务统计"""
        # 获取用户名
        user_result = await db.execute(
            select(User).where(User.id == user_id)
        )
        user = user_result.scalar_one_or_none()
        user_name = user.name if user else None

        # 统计该用户的任务
        total_result = await db.execute(
            select(func.count(Task.id)).where(
                and_(
                    Task.assignee_ids.like(f"%{user_id}%"),
                    Task.parent_id == None
                )
            )
        )
        total_tasks = total_result.scalar() or 0

        # 统计各状态数量
        status_counts = {}
        for status in ["todo", "in_progress", "done"]:
            result = await db.execute(
                select(func.count(Task.id)).where(
                    and_(
                        Task.assignee_ids.like(f"%{user_id}%"),
                        Task.status == status,
                        Task.parent_id == None
                    )
                )
            )
            status_counts[status] = result.scalar() or 0

        # 计算过期任务
        today = datetime.now().strftime("%Y-%m-%d")
        overdue_result = await db.execute(
            select(func.count(Task.id)).where(
                and_(
                    Task.assignee_ids.like(f"%{user_id}%"),
                    Task.due_date < today,
                    Task.status.in_(["todo", "in_progress"]),
                    Task.parent_id == None
                )
            )
        )
        overdue_count = overdue_result.scalar() or 0

        # 计算完成率
        completion_rate = (status_counts.get("done", 0) / total_tasks * 100) if total_tasks > 0 else 0

        return {
            "userId": user_id,
            "userName": user_name,
            "totalTasks": total_tasks,
            "todoCount": status_counts.get("todo", 0),
            "inProgressCount": status_counts.get("in_progress", 0),
            "doneCount": status_counts.get("done", 0),
            "overdueCount": overdue_count,
            "completionRate": round(completion_rate, 2)
        }


# 全局服务实例
task_service = TaskService()
