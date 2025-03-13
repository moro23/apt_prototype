from typing import Any, List

from db.session import get_db
from domains.appraisal.schemas import department_group as schemas
from domains.appraisal.services.department_group import department_group_service as actions
from domains.auth.models.users import User
from fastapi import APIRouter, Depends
from fastapi import HTTPException
from pydantic import UUID4
from sqlalchemy.orm import Session
from starlette.status import HTTP_201_CREATED, HTTP_404_NOT_FOUND
from utils.rbac import get_current_user
from utils.schemas import HTTPError

department_group_router = APIRouter(prefix='/department_groups')


@department_group_router.get(
    "/",
    response_model=List[schemas.DepartmentGroupSchema]
)
async def list_department_groups(
        db: Session = Depends(get_db),
        current_user: User = Depends(get_current_user),
        skip: int = 0,
        limit: int = 100
) -> Any:
    department_groups = await actions.list_department_groups(db=db, skip=skip, limit=limit)
    return department_groups


@department_group_router.post(
    "/",
    response_model=schemas.DepartmentGroupSchema,
    status_code=HTTP_201_CREATED
)
async def create_department_group(
        *, db: Session = Depends(get_db),
        current_user: User = Depends(get_current_user),
        department_group_in: schemas.DepartmentGroupCreate
) -> Any:
    department_group = await actions.create_department_group(db=db, department_group_in=department_group_in)
    return department_group


@department_group_router.put(
    "/{id}",
    response_model=schemas.DepartmentGroupSchema,
    responses={HTTP_404_NOT_FOUND: {"model": HTTPError}},
)
async def update_department_group(
        *, db: Session = Depends(get_db),
        current_user: User = Depends(get_current_user),
        id: UUID4,
        department_group_in: schemas.DepartmentGroupUpdate,
) -> Any:
    department_group = await actions.get_department_group(db=db, id=id)
    if not department_group:
        raise HTTPException(
            status_code=HTTP_404_NOT_FOUND,
            detail="Department group not found"
        )
    department_group = await actions.update_department_group(
        db=db, id=department_group.id, department_group_in=department_group_in
    )
    return department_group


@department_group_router.get(
    "/{id}",
    response_model=schemas.DepartmentGroupSchema,
    responses={HTTP_404_NOT_FOUND: {"model": HTTPError}},
)
async def get_department_group(
        *, db: Session = Depends(get_db),
        current_user: User = Depends(get_current_user),
        id: UUID4
) -> Any:
    department_group = await actions.get_department_group(db=db, id=id)
    if not department_group:
        raise HTTPException(
            status_code=HTTP_404_NOT_FOUND,
            detail="Department group not found"
        )
    return department_group


@department_group_router.delete(
    "/{id}",
    response_model=dict[str, Any],
    responses={HTTP_404_NOT_FOUND: {"model": HTTPError}},
)
async def delete_department_group(
        *, db: Session = Depends(get_db),
        current_user: User = Depends(get_current_user),
        id: UUID4
) -> Any:
    department_group = await actions.get_department_group(db=db, id=id)
    if not department_group:
        raise HTTPException(
            status_code=HTTP_404_NOT_FOUND,
            detail="Department group not found"
        )
    department_group = await actions.delete_department_group(db=db, id=id)
    return department_group
