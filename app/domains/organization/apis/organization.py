from typing import Any, List, Literal

from fastapi import APIRouter, Depends, status
from pydantic import UUID4
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import Session

from db.session import get_db
from domains.auth.models import User
from domains.organization.schemas import organization as schemas
from domains.organization.services.organization import organization_service as actions
from utils.rbac import check_if_is_system_admin
from utils.schemas import HTTPError

organization_router = APIRouter()


@organization_router.get(
    "/",
    response_model=List[schemas.OrganizationSchema],
)
# @ContentQueryChecker(organizations.model.c(), None)
async def list_organizations(
        *, db: AsyncSession = Depends(get_db),
        current_user: User = Depends(check_if_is_system_admin),
        skip: int = 0,
        limit: int = 100,
        order_by: str | None = None,
        order_direction: Literal['asc', 'desc'] = 'asc'
) -> Any:
    organizations = await actions.list_organizations(
        db=db, skip=skip, limit=limit, order_by=order_by, order_direction=order_direction
    )
    return organizations


@organization_router.post(
    "/",
    response_model=schemas.OrganizationSchema,
    status_code=status.HTTP_201_CREATED,
)
async def create_organization(
        *,
        db: AsyncSession = Depends(get_db),
        current_user: User = Depends(check_if_is_system_admin),
        data: schemas.OrganizationCreate
) -> Any:
    organization = await actions.create_organization(data=data, db=db)
    return organization


@organization_router.put(
    "/{id}",
    response_model=schemas.OrganizationSchema,
    responses={status.HTTP_404_NOT_FOUND: {"model": HTTPError}},
)
async def update_organization(
        *, db: Session = Depends(get_db),
        current_user: User = Depends(check_if_is_system_admin),
        id: UUID4,
        organization_in: schemas.OrganizationUpdate,
) -> Any:
    organization = await actions.update_organization(id=id, data=organization_in, db=db)
    return organization


@organization_router.get(
    "/{id}",
    response_model=schemas.OrganizationWithUsersResponse,
    responses={status.HTTP_404_NOT_FOUND: {"model": HTTPError}},
)
async def get_organization(
        *, db: AsyncSession = Depends(get_db),
        current_user: User = Depends(check_if_is_system_admin),
        id: UUID4,
        
) -> Any:
    organization = await actions.get_organization(db=db, id=id)
    return organization


@organization_router.delete(
    "/{id}",
    status_code=status.HTTP_204_NO_CONTENT,
    responses={status.HTTP_404_NOT_FOUND: {"model": HTTPError}},
)
async def delete_organization(
        *, db: Session = Depends(get_db),
        current_user: User = Depends(check_if_is_system_admin),
        id: UUID4,
        soft_delete: bool = False
) -> None:
    await actions.delete_organization(db=db, id=id, soft_delete=soft_delete)


@organization_router.post(
    "/reactivate_organization/{id}",
    responses={status.HTTP_404_NOT_FOUND: {"model": HTTPError}},
)
async def reactivate_organization(
        *, db: AsyncSession = Depends(get_db),
        current_user: User = Depends(check_if_is_system_admin),
        id: UUID4
) -> Any:
    organization = await actions.reactivate_organization(id=id, db=db)
    return organization
