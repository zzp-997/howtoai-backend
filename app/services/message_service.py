"""
消息服务 - 消息中心业务逻辑
"""
from typing import List, Optional, Dict, Any
from datetime import datetime
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func, and_
from app.models import Message
from app.schemas.message import MessageCreate, MessageQuery


class MessageService:
    """消息服务类"""

    async def create_message(self, db: AsyncSession, message_data: MessageCreate) -> Message:
        """
        创建消息

        Args:
            db: 数据库会话
            message_data: 消息创建数据

        Returns:
            创建的消息对象
        """
        message = Message(
            user_id=message_data.user_id,
            type=message_data.type,
            title=message_data.title,
            content=message_data.content,
            related_type=message_data.related_type,
            related_id=message_data.related_id,
            is_read=False
        )
        db.add(message)
        await db.commit()
        await db.refresh(message)
        return message

    async def get_messages(
        self, db: AsyncSession, user_id: int, query: MessageQuery
    ) -> Dict[str, Any]:
        """
        获取用户消息列表（分页）

        Args:
            db: 数据库会话
            user_id: 用户ID
            query: 查询参数

        Returns:
            分页结果，包含消息列表和总数
        """
        # 构建查询条件
        conditions = [Message.user_id == user_id]

        if query.type:
            conditions.append(Message.type == query.type)
        if query.is_read is not None:
            conditions.append(Message.is_read == query.is_read)
        if query.related_type:
            conditions.append(Message.related_type == query.related_type)
        if query.related_id is not None:
            conditions.append(Message.related_id == query.related_id)

        # 查询总数
        count_query = select(func.count()).select_from(Message).where(and_(*conditions))
        total_result = await db.execute(count_query)
        total = total_result.scalar() or 0

        # 计算分页
        page = query.page if query.page > 0 else 1
        page_size = query.page_size if query.page_size > 0 else 20
        offset = (page - 1) * page_size

        # 查询消息列表
        select_query = (
            select(Message)
            .where(and_(*conditions))
            .order_by(Message.created_at.desc())
            .offset(offset)
            .limit(page_size)
        )
        result = await db.execute(select_query)
        messages = result.scalars().all()

        return {
            "items": messages,
            "total": total,
            "page": page,
            "page_size": page_size,
            "total_pages": (total + page_size - 1) // page_size if page_size > 0 else 0
        }

    async def get_unread_count(self, db: AsyncSession, user_id: int, msg_type: Optional[str] = None) -> int:
        """
        获取未读消息数量

        Args:
            db: 数据库会话
            user_id: 用户ID
            msg_type: 消息类型（可选，用于筛选特定类型）

        Returns:
            未读消息数量
        """
        conditions = [Message.user_id == user_id, Message.is_read == False]

        if msg_type:
            conditions.append(Message.type == msg_type)

        query = select(func.count()).select_from(Message).where(and_(*conditions))
        result = await db.execute(query)
        return result.scalar() or 0

    async def mark_as_read(self, db: AsyncSession, message_id: int, user_id: int) -> Optional[Message]:
        """
        标记消息为已读

        Args:
            db: 数据库会话
            message_id: 消息ID
            user_id: 用户ID（用于验证消息所属权）

        Returns:
            更新后的消息对象，如果不存在或无权操作则返回None
        """
        # 查询消息
        result = await db.execute(
            select(Message).where(and_(
                Message.id == message_id,
                Message.user_id == user_id
            ))
        )
        message = result.scalar_one_or_none()

        if not message:
            return None

        # 如果已经是已读状态，直接返回
        if message.is_read:
            return message

        # 更新为已读
        message.is_read = True
        message.read_at = datetime.utcnow()
        await db.commit()
        await db.refresh(message)
        return message

    async def mark_all_as_read(self, db: AsyncSession, user_id: int, msg_type: Optional[str] = None) -> int:
        """
        标记所有消息为已读

        Args:
            db: 数据库会话
            user_id: 用户ID
            msg_type: 消息类型（可选，用于筛选特定类型）

        Returns:
            实际更新的消息数量
        """
        conditions = [Message.user_id == user_id, Message.is_read == False]

        if msg_type:
            conditions.append(Message.type == msg_type)

        # 查询所有未读消息
        query = select(Message).where(and_(*conditions))
        result = await db.execute(query)
        messages = result.scalars().all()

        if not messages:
            return 0

        now = datetime.utcnow()
        for message in messages:
            message.is_read = True
            message.read_at = now

        await db.commit()
        return len(messages)


# 全局服务实例
message_service = MessageService()
