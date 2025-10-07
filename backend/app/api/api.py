from fastapi import APIRouter
from app.api.endpoints import users, admins, password_reset

api_router = APIRouter()

api_router.include_router(users.router, prefix="/users", tags=["users"])
api_router.include_router(admins.router, prefix="/admins", tags=["admins"])
api_router.include_router(password_reset.router, prefix="/password", tags=["password-reset"])