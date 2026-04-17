"""
API 路由导出
"""
from fastapi import APIRouter
from app.api.v1.auth import router as auth_router
from app.api.v1.users import router as users_router
from app.api.v1.meeting_rooms import router as meeting_room_router
from app.api.v1.reservations import router as reservation_router
from app.api.v1.trips import router as trip_router
from app.api.v1.leaves import router as leave_router
from app.api.v1.attendance import router as attendance_router
from app.api.v1.todos import router as todo_router
from app.api.v1.announcements import router as announcement_router
from app.api.v1.documents import router as document_router
from app.api.v1.expenses import router as expense_router
from app.api.v1.configs import router as config_router

# v1 版本路由
api_router = APIRouter(prefix="/v1")
api_router.include_router(auth_router)
api_router.include_router(users_router)
api_router.include_router(meeting_room_router)
api_router.include_router(reservation_router)
api_router.include_router(trip_router)
api_router.include_router(leave_router)
api_router.include_router(attendance_router)
api_router.include_router(todo_router)
api_router.include_router(announcement_router)
api_router.include_router(document_router)
api_router.include_router(expense_router)
api_router.include_router(config_router)

__all__ = ["api_router"]