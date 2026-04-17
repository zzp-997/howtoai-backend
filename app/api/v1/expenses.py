"""
报销单 API
"""
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from typing import List
import json
from app.core.database import get_db
from app.schemas import ExpenseClaimCreate, ExpenseClaimUpdate, ExpenseClaimResponse, ResponseModel
from app.services import expense_claim_service
from app.api.v1.auth import get_current_user
from app.schemas.user import UserResponse

router = APIRouter(prefix="/expenses", tags=["报销单"])


@router.get("", response_model=ResponseModel[List[ExpenseClaimResponse]])
async def get_expenses(
    status: str = None,
    db: AsyncSession = Depends(get_db),
    current_user: UserResponse = Depends(get_current_user)
):
    """获取报销单列表"""
    if current_user.role == "admin" and status:
        expenses = await expense_claim_service.find_by_status(db, status)
    else:
        expenses = await expense_claim_service.find_by_user(db, current_user.id)
    return ResponseModel(data=expenses)


@router.get("/{expense_id}", response_model=ResponseModel[ExpenseClaimResponse])
async def get_expense(
    expense_id: int,
    db: AsyncSession = Depends(get_db),
    current_user: UserResponse = Depends(get_current_user)
):
    """获取报销单详情"""
    expense = await expense_claim_service.get_by_id(db, expense_id)
    if not expense:
        raise HTTPException(status_code=404, detail="报销单不存在")
    return ResponseModel(data=expense)


@router.post("", response_model=ResponseModel[ExpenseClaimResponse])
async def create_expense(
    data: ExpenseClaimCreate,
    db: AsyncSession = Depends(get_db),
    current_user: UserResponse = Depends(get_current_user)
):
    """创建报销单"""
    expense = await expense_claim_service.create(db, {
        **data.model_dump(),
        "userId": current_user.id,
        "expenses": json.dumps([e.model_dump() for e in data.expenses]) if data.expenses else "[]"
    })
    return ResponseModel(data=expense)


@router.put("/{expense_id}", response_model=ResponseModel[ExpenseClaimResponse])
async def update_expense(
    expense_id: int,
    data: ExpenseClaimUpdate,
    db: AsyncSession = Depends(get_db),
    current_user: UserResponse = Depends(get_current_user)
):
    """更新报销单"""
    expense = await expense_claim_service.get_by_id(db, expense_id)
    if not expense:
        raise HTTPException(status_code=404, detail="报销单不存在")
    if expense.userId != current_user.id:
        raise HTTPException(status_code=403, detail="无权限")
    if expense.status != "draft":
        raise HTTPException(status_code=400, detail="只能修改草稿状态的报销单")

    update_data = data.model_dump(exclude_unset=True)
    if data.expenses:
        update_data["expenses"] = json.dumps([e.model_dump() for e in data.expenses])

    updated = await expense_claim_service.update(db, expense_id, update_data)
    return ResponseModel(data=updated)


@router.post("/{expense_id}/submit", response_model=ResponseModel[ExpenseClaimResponse])
async def submit_expense(
    expense_id: int,
    db: AsyncSession = Depends(get_db),
    current_user: UserResponse = Depends(get_current_user)
):
    """提交报销单"""
    expense = await expense_claim_service.get_by_id(db, expense_id)
    if not expense:
        raise HTTPException(status_code=404, detail="报销单不存在")
    if expense.userId != current_user.id:
        raise HTTPException(status_code=403, detail="无权限")
    if expense.status != "draft":
        raise HTTPException(status_code=400, detail="只能提交草稿状态的报销单")

    updated = await expense_claim_service.submit(db, expense_id)
    return ResponseModel(data=updated, message="提交成功")


@router.post("/{expense_id}/approve", response_model=ResponseModel[ExpenseClaimResponse])
async def approve_expense(
    expense_id: int,
    db: AsyncSession = Depends(get_db),
    current_user: UserResponse = Depends(get_current_user)
):
    """审批报销单（管理员）"""
    if current_user.role != "admin":
        raise HTTPException(status_code=403, detail="无权限")

    expense = await expense_claim_service.approve(db, expense_id, current_user.id)
    if not expense:
        raise HTTPException(status_code=404, detail="报销单不存在")
    return ResponseModel(data=expense, message="审批成功")


@router.delete("/{expense_id}")
async def delete_expense(
    expense_id: int,
    db: AsyncSession = Depends(get_db),
    current_user: UserResponse = Depends(get_current_user)
):
    """删除报销单"""
    expense = await expense_claim_service.get_by_id(db, expense_id)
    if not expense:
        raise HTTPException(status_code=404, detail="报销单不存在")
    if expense.userId != current_user.id:
        raise HTTPException(status_code=403, detail="无权限")
    if expense.status != "draft":
        raise HTTPException(status_code=400, detail="只能删除草稿状态的报销单")

    await expense_claim_service.delete(db, expense_id)
    return ResponseModel(message="删除成功")