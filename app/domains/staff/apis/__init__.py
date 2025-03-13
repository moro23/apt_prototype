from fastapi import APIRouter

from .department import department_router
from .staff import staff_router

staff_routers = APIRouter(prefix='/staff')
staff_routers.include_router(department_router, tags=["STAFF DEPARTMENTS"])
staff_routers.include_router(staff_router, tags=["STAFF"])
