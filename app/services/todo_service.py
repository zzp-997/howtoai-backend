"""
待办事项服务
"""
from typing import List, Optional
from datetime import datetime
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from app.models import Todo
from app.services.base import BaseService


class TodoService(BaseService[Todo]):
    """待办事项服务"""

    def __init__(self):
        super().__init__(Todo)

    async def find_by_user(self, db: AsyncSession, user_id: int) -> List[Todo]:
        """查询用户待办"""
        result = await db.execute(
            select(Todo).where(Todo.userId == user_id).order_by(Todo.createdAt.desc())
        )
        return result.scalars().all()

    async def find_pending(self, db: AsyncSession, user_id: int) -> List[Todo]:
        """查询未完成待办"""
        result = await db.execute(
            select(Todo).where(
                Todo.userId == user_id,
                Todo.status == "pending"
            ).order_by(Todo.dueDate, Todo.priority)
        )
        return result.scalars().all()

    async def find_completed(self, db: AsyncSession, user_id: int) -> List[Todo]:
        """查询已完成待办"""
        result = await db.execute(
            select(Todo).where(
                Todo.userId == user_id,
                Todo.status == "completed"
            ).order_by(Todo.completedAt.desc())
        )
        return result.scalars().all()

    async def toggle_complete(self, db: AsyncSession, id: int) -> Optional[Todo]:
        """切换完成状态"""
        todo = await self.get_by_id(db, id)
        if not todo:
            return None

        new_status = "completed" if todo.status == "pending" else "pending"
        completed_at = datetime.now() if new_status == "completed" else None

        return await self.update(db, id, {"status": new_status, "completedAt": completed_at})

    async def count_pending(self, db: AsyncSession, user_id: int) -> int:
        """统计未完成数量"""
        result = await db.execute(
            select(Todo).where(Todo.userId == user_id, Todo.status == "pending")
        )
        return len(result.scalars().all())

    async def find_upcoming(self, db: AsyncSession, user_id: int) -> List[Todo]:
        """查询即将到期的待办"""
        today = datetime.now().strftime("%Y-%m-%d")
        tomorrow = datetime.now().strftime("%Y-%m-%d")  # 简化处理
        result = await db.execute(
            select(Todo).where(
                Todo.userId == user_id,
                Todo.status == "pending",
                Todo.dueDate.in_([today, tomorrow])
            ).order_by(Todo.dueDate)
        )
        return result.scalars().all()


todo_service = TodoService()