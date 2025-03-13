from typing import Any, List, Literal

from fastapi import APIRouter, Depends, status
from pydantic import UUID4
from sqlalchemy.orm import Session

from db.session import get_db
from domains.auth.models import User
from domains.organization.schemas import tenancy as schemas
from domains.organization.services.tenancy import tenancy_service as actions
from utils.rbac import get_current_user
from utils.schemas import HTTPError

tenancy_router = APIRouter(prefix="/tenancies")


@tenancy_router.get(
    "/",
    response_model=List[schemas.TenancySchema],
)
async def list_tenancies(
        *, db: Session = Depends(get_db),
        current_user: User = Depends(get_current_user),
        skip: int = 0,
        limit: int = 100,
        order_by: str | None = None,
        order_direction: Literal['asc', 'desc'] = 'asc'
) -> Any:
    tenancies = await actions.list_tenancies(
        db=db, skip=skip, limit=limit, order_by=order_by, order_direction=order_direction
    )
    return tenancies


@tenancy_router.post(
    "/",
    response_model=schemas.TenancySchema,
    status_code=status.HTTP_201_CREATED,
)
async def create_tenancy(
        *, db: Session = Depends(get_db),
        current_user: User = Depends(get_current_user),
        tenancy_in: schemas.TenancyCreate
) -> Any:
    tenancy = await actions.create_tenancy(db=db, tenancy_in=tenancy_in)
    return tenancy


@tenancy_router.put(
    "/{id}",
    response_model=schemas.TenancySchema,
    responses={status.HTTP_404_NOT_FOUND: {"model": HTTPError}},
)
async def update_tenancy(
        *, db: Session = Depends(get_db),
        current_user: User = Depends(get_current_user),
        id: UUID4,
        tenancy_in: schemas.TenancyUpdate,
) -> Any:
    tenancy = await actions.update_tenancy(db=db, id=id, tenancy_in=tenancy_in)
    return tenancy


@tenancy_router.get(
    "/{id}",
    response_model=schemas.TenancySchema,
    responses={status.HTTP_404_NOT_FOUND: {"model": HTTPError}},
)
async def get_tenancy(
        *, db: Session = Depends(get_db),
        current_user: User = Depends(get_current_user),
        id: UUID4
) -> Any:
    tenancy = await actions.get_tenancy(db=db, id=id)
    return tenancy


@tenancy_router.delete(
    "/{id}",
    status_code=status.HTTP_204_NO_CONTENT,
    responses={status.HTTP_404_NOT_FOUND: {"model": HTTPError}},
)
async def delete_tenancy(
        *, db: Session = Depends(get_db),
        current_user: User = Depends(get_current_user),
        id: UUID4
) -> None:
    await actions.delete_tenancy(db=db, id=id)
