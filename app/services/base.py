"""
基础服务类 - 提供 CRUD 操作
"""
from typing import TypeVar, Generic, Type, Optional, List, Any
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func
from sqlalchemy.inspection import inspect
from app.core.database import Base

ModelType = TypeVar("ModelType", bound=Base)


class BaseService(Generic[ModelType]):
    """基础服务类"""

    def __init__(self, model: Type[ModelType]):
        self.model = model
        # 获取主键信息
        mapper = inspect(model)
        pk_list = mapper.primary_key
        self.primary_key = pk_list[0] if pk_list else None
        self.pk_name = self.primary_key.name if self.primary_key is not None else "id"

    async def get_by_id(self, db: AsyncSession, id: Any) -> Optional[ModelType]:
        """根据主键查询"""
        if self.primary_key is None:
            return None
        result = await db.execute(select(self.model).where(self.primary_key == id))
        return result.scalar_one_or_none()

    async def get_all(self, db: AsyncSession) -> List[ModelType]:
        """查询所有"""
        result = await db.execute(select(self.model))
        return result.scalars().all()

    async def create(self, db: AsyncSession, obj_in: dict) -> ModelType:
        """创建"""
        db_obj = self.model(**obj_in)
        db.add(db_obj)
        await db.commit()
        await db.refresh(db_obj)
        return db_obj

    async def update(self, db: AsyncSession, id: Any, obj_in: dict) -> Optional[ModelType]:
        """更新"""
        db_obj = await self.get_by_id(db, id)
        if not db_obj:
            return None
        for key, value in obj_in.items():
            if value is not None:
                setattr(db_obj, key, value)
        await db.commit()
        await db.refresh(db_obj)
        return db_obj

    async def delete(self, db: AsyncSession, id: Any) -> bool:
        """删除"""
        db_obj = await self.get_by_id(db, id)
        if not db_obj:
            return False
        await db.delete(db_obj)
        await db.commit()
        return True

    async def count(self, db: AsyncSession) -> int:
        """统计数量"""
        result = await db.execute(select(func.count()).select_from(self.model))
        return result.scalar() or 0