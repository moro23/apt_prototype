from typing import Any, List, Literal

from fastapi import APIRouter, Depends, status
from pydantic import UUID4
from sqlalchemy.ext.asyncio import AsyncSession

from db.session import get_db
from domains.auth.models import User
from domains.staff.schemas import department as schemas
from domains.staff.services.department import department_service as actions
from utils.rbac import get_current_user
from utils.schemas import HTTPError

department_router = APIRouter(prefix='/departments')


@department_router.get(
    "/",
    response_model=List[schemas.DepartmentSchema],
)
async def list_departments(
        *, db: AsyncSession = Depends(get_db),
        current_user: User = Depends(get_current_user),
        skip: int = 0,
        limit: int = 100,
        order_by: str | None = None,
        order_direction: Literal['asc', 'desc'] = 'asc'
) -> Any:
    departments = await actions.list_departments(
        db=db, skip=skip, limit=limit, order_by=order_by, order_direction=order_direction
    )
    return departments


@department_router.post(
    "/",
    response_model=schemas.DepartmentSchema,
    status_code=status.HTTP_201_CREATED,
)
async def create_department(
        *, db: AsyncSession = Depends(get_db),
        current_user: User = Depends(get_current_user),
        department_in: schemas.DepartmentCreate
) -> Any:
    department = await actions.create_department(db=db, department_in=department_in)
    return department


@department_router.put(
    "/{id}",
    response_model=schemas.DepartmentSchema,
    responses={status.HTTP_404_NOT_FOUND: {"model": HTTPError}},
)
async def update_department(
        *, db: AsyncSession = Depends(get_db),
        current_user: User = Depends(get_current_user),
        id: UUID4,
        department_in: schemas.DepartmentUpdate,
) -> Any:
    department = await actions.update_department(db=db, id=id, department_in=department_in)
    return department


@department_router.get(
    "/{id}",
    response_model=schemas.DepartmentSchema,
    responses={status.HTTP_404_NOT_FOUND: {"model": HTTPError}},
)
async def get_department(
        *, db: AsyncSession = Depends(get_db),
        current_user: User = Depends(get_current_user),
        id: UUID4
) -> Any:
    department = await actions.get_department(db=db, id=id)
    return department


@department_router.delete(
    "/{id}",
    status_code=status.HTTP_204_NO_CONTENT,
)
async def delete_department(
        *, db: AsyncSession = Depends(get_db),
        current_user: User = Depends(get_current_user),
        id: UUID4
) -> None:
    await actions.delete_department(db=db, id=id)
