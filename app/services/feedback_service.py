"""
意见反馈服务
"""
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, and_, or_
from datetime import datetime
from typing import Optional, List, Dict
import logging
import uuid

from app.models.feedback import Feedback
from app.schemas.feedback import FeedbackCreate, FeedbackReplySchema, FeedbackQuerySchema

logger = logging.getLogger(__name__)


class FeedbackService:
    """意见反馈服务类"""

    @staticmethod
    def _generate_feedback_no() -> str:
        """生成反馈编号"""
        timestamp = datetime.now().strftime("%Y%m%d%H%M%S")
        unique_id = str(uuid.uuid4())[:8]
        return f"FB{timestamp}{unique_id.upper()}"

    async def submit(self, db: AsyncSession, user_id: int, user_name: str,
                     feedback_data: FeedbackCreate) -> Dict:
        """
        用户提交反馈

        Args:
            db: 数据库会话
            user_id: 用户ID
            user_name: 用户名
            feedback_data: 反馈数据

        Returns:
            提交结果
        """
        feedback = Feedback(
            feedback_no=self._generate_feedback_no(),
            user_id=user_id,
            user_name=user_name,
            type=feedback_data.type,
            title=feedback_data.title,
            content=feedback_data.content,
            images=feedback_data.images,
            status="pending"
        )

        db.add(feedback)
        await db.commit()
        await db.refresh(feedback)

        logger.info(f"用户 {user_id} 提交反馈成功，反馈编号: {feedback.feedback_no}")

        return {
            "success": True,
            "message": "反馈提交成功",
            "data": {
                "id": feedback.id,
                "feedback_no": feedback.feedback_no,
                "status": feedback.status
            }
        }

    async def reply(self, db: AsyncSession, feedback_id: int, handler_id: int,
                    handler_name: str, reply_data: FeedbackReplySchema) -> Dict:
        """
        管理员回复反馈

        Args:
            db: 数据库会话
            feedback_id: 反馈ID
            handler_id: 处理人ID
            handler_name: 处理人姓名
            reply_data: 回复内容

        Returns:
            回复结果
        """
        result = await db.execute(
            select(Feedback).where(Feedback.id == feedback_id)
        )
        feedback = result.scalar_one_or_none()

        if not feedback:
            return {
                "success": False,
                "message": "反馈不存在"
            }

        if feedback.status == "closed":
            return {
                "success": False,
                "message": "反馈已关闭，无法回复"
            }

        feedback.handler_id = handler_id
        feedback.handler_name = handler_name
        feedback.reply_content = reply_data.reply_content
        feedback.replied_at = datetime.now()
        feedback.status = "replied"

        await db.commit()

        logger.info(f"管理员 {handler_name} 回复反馈 {feedback.feedback_no} 成功")

        return {
            "success": True,
            "message": "回复成功",
            "data": {
                "id": feedback.id,
                "feedback_no": feedback.feedback_no,
                "status": feedback.status,
                "reply_content": feedback.reply_content,
                "replied_at": feedback.replied_at
            }
        }

    async def get_by_id(self, db: AsyncSession, feedback_id: int) -> Optional[Feedback]:
        """
        获取反馈详情

        Args:
            db: 数据库会话
            feedback_id: 反馈ID

        Returns:
            反馈详情
        """
        result = await db.execute(
            select(Feedback).where(Feedback.id == feedback_id)
        )
        return result.scalar_one_or_none()

    async def get_by_no(self, db: AsyncSession, feedback_no: str) -> Optional[Feedback]:
        """
        根据反馈编号获取反馈

        Args:
            db: 数据库会话
            feedback_no: 反馈编号

        Returns:
            反馈详情
        """
        result = await db.execute(
            select(Feedback).where(Feedback.feedback_no == feedback_no)
        )
        return result.scalar_one_or_none()

    async def query(self, db: AsyncSession, query_params: FeedbackQuerySchema,
                    is_admin: bool = False) -> Dict:
        """
        查询反馈列表

        Args:
            db: 数据库会话
            query_params: 查询参数
            is_admin: 是否为管理员查询

        Returns:
            查询结果
        """
        # 构建查询条件
        conditions = []

        if not is_admin and query_params.user_id:
            # 普通用户只能查看自己的反馈
            conditions.append(Feedback.user_id == query_params.user_id)
        elif not is_admin and not query_params.user_id:
            # 普通用户未指定user_id时，默认查询自己的
            pass
        else:
            # 管理员可以按user_id查询
            if query_params.user_id:
                conditions.append(Feedback.user_id == query_params.user_id)

        # 按类型筛选
        if query_params.type:
            conditions.append(Feedback.type == query_params.type)

        # 按状态筛选
        if query_params.status:
            conditions.append(Feedback.status == query_params.status)

        # 按关键词搜索（标题或内容）
        if query_params.keyword:
            keyword_pattern = f"%{query_params.keyword}%"
            conditions.append(
                or_(
                    Feedback.title.ilike(keyword_pattern),
                    Feedback.content.ilike(keyword_pattern)
                )
            )

        # 按时间范围筛选
        if query_params.start_date:
            conditions.append(Feedback.created_at >= query_params.start_date)
        if query_params.end_date:
            conditions.append(Feedback.created_at <= query_params.end_date)

        # 执行查询
        query = select(Feedback)
        if conditions:
            query = query.where(and_(*conditions))

        query = query.order_by(Feedback.created_at.desc())

        result = await db.execute(query)
        feedbacks = result.scalars().all()

        return {
            "success": True,
            "data": [
                {
                    "id": fb.id,
                    "feedback_no": fb.feedback_no,
                    "user_id": fb.user_id,
                    "user_name": fb.user_name,
                    "type": fb.type,
                    "title": fb.title,
                    "content": fb.content,
                    "images": fb.images,
                    "status": fb.status,
                    "handler_id": fb.handler_id,
                    "handler_name": fb.handler_name,
                    "reply_content": fb.reply_content,
                    "replied_at": fb.replied_at,
                    "closed_at": fb.closed_at,
                    "created_at": fb.created_at,
                    "updated_at": fb.updated_at
                }
                for fb in feedbacks
            ],
            "total": len(feedbacks)
        }

    async def close(self, db: AsyncSession, feedback_id: int,
                    handler_id: int, handler_name: str) -> Dict:
        """
        关闭反馈

        Args:
            db: 数据库会话
            feedback_id: 反馈ID
            handler_id: 处理人ID
            handler_name: 处理人姓名

        Returns:
            关闭结果
        """
        result = await db.execute(
            select(Feedback).where(Feedback.id == feedback_id)
        )
        feedback = result.scalar_one_or_none()

        if not feedback:
            return {
                "success": False,
                "message": "反馈不存在"
            }

        if feedback.status == "closed":
            return {
                "success": False,
                "message": "反馈已关闭"
            }

        feedback.status = "closed"
        feedback.closed_at = datetime.now()
        feedback.handler_id = handler_id
        feedback.handler_name = handler_name

        await db.commit()

        logger.info(f"管理员 {handler_name} 关闭反馈 {feedback.feedback_no} 成功")

        return {
            "success": True,
            "message": "反馈已关闭",
            "data": {
                "id": feedback.id,
                "feedback_no": feedback.feedback_no,
                "status": feedback.status,
                "closed_at": feedback.closed_at
            }
        }


# 全局服务实例
feedback_service = FeedbackService()
