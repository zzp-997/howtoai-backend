"""
报销单相关 Schema
"""
import json
from pydantic import field_validator
from typing import Optional, List
from datetime import datetime
from app.schemas.common import CamelModel


class ExpenseItem(CamelModel):
    """费用明细项"""
    category: str  # 交通/住宿/餐饮/其他
    estimated: float = 0
    actual: float = 0
    description: Optional[str] = None


class ExpenseClaimBase(CamelModel):
    """报销单基础"""
    trip_id: Optional[int] = None
    expenses: List[ExpenseItem] = []
    total_estimated: float = 0
    total_actual: float = 0


class ExpenseClaimCreate(ExpenseClaimBase):
    """创建报销单"""
    pass


class ExpenseClaimUpdate(CamelModel):
    """更新报销单"""
    expenses: Optional[List[ExpenseItem]] = None
    total_estimated: Optional[float] = None
    total_actual: Optional[float] = None


class ExpenseClaimResponse(ExpenseClaimBase):
    """报销单响应"""
    id: int
    user_id: int
    status: str = "draft"
    submitted_at: Optional[datetime] = None
    approved_by: Optional[int] = None
    approved_at: Optional[datetime] = None
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None

    @field_validator('expenses', mode='before')
    @classmethod
    def parse_expenses(cls, v):
        """解析 expenses 字段，支持 JSON 字符串"""
        if v is None:
            return []
        if isinstance(v, list):
            return v
        if isinstance(v, str):
            try:
                return json.loads(v)
            except:
                return []
        return []
