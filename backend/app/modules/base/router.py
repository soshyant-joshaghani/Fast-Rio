from fastapi import APIRouter

from app.modules.base.auth.router import auth_router
from app.modules.base.users.router.admin import users_router_admin

base_router = APIRouter(prefix="/base")

# Auth — single login endpoint for all users including SuperAdmin
base_router.include_router(auth_router)
base_router.include_router(users_router_admin)
