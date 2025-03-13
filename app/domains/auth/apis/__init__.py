from fastapi import APIRouter

from .email_router import email_router
from .login import auth_router
from .logout import logout_auth_router
from .roles import role_router
from .user_account import users_router

prefix = '/auth'
auth_routers = APIRouter()
# auth_routers.include_router(email_router, tags=["EMAIL SERVICE"])
auth_routers.include_router(auth_router, prefix=prefix, tags=['AUTHENTICATION'])
auth_routers.include_router(logout_auth_router, prefix=prefix, tags=['AUTHENTICATION'])
auth_routers.include_router(users_router, prefix=f'/users', tags=["USERS ACCOUNTS"])
auth_routers.include_router(role_router, tags=["ORGANIZATION ROLES"])
