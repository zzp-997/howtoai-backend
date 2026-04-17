"""
报销单相关 Schema
"""
import json
from pydantic import BaseModel, field_validator
from typing import Optional, List
from datetime import datetime


class ExpenseItem(BaseModel):
    """费用明细项"""
    category: str  # 交通/住宿/餐饮/其他
    estimated: float = 0
    actual: float = 0
    description: Optional[str] = None


class ExpenseClaimBase(BaseModel):
    """报销单基础"""
    tripId: Optional[int] = None
    expenses: List[ExpenseItem] = []
    totalEstimated: float = 0
    totalActual: float = 0


class ExpenseClaimCreate(ExpenseClaimBase):
    """创建报销单"""
    pass


class ExpenseClaimUpdate(BaseModel):
    """更新报销单"""
    expenses: Optional[List[ExpenseItem]] = None
    totalEstimated: Optional[float] = None
    totalActual: Optional[float] = None


class ExpenseClaimResponse(ExpenseClaimBase):
    """报销单响应"""
    id: int
    userId: int
    status: str = "draft"
    submittedAt: Optional[datetime] = None
    approvedBy: Optional[int] = None
    approvedAt: Optional[datetime] = None
    createdAt: Optional[datetime] = None
    updatedAt: Optional[datetime] = None

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

    class Config:
        from_attributes = True