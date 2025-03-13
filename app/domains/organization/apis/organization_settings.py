from typing import Any, List, Literal

from fastapi import APIRouter, Depends, status
from pydantic import UUID4
from sqlalchemy.orm import Session

from db.session import get_db
from domains.auth.models import User
from domains.organization.schemas import organization_settings as schemas
from domains.organization.services.organization_settings import organization_settings_service as actions
from utils.rbac import get_current_user
from utils.schemas import HTTPError

organization_settings_router = APIRouter(prefix="/setting")


@organization_settings_router.get(
    "/",
    response_model=List[schemas.OrganizationSettingsSchema],
)
async def list_organization_setting(
        *, db: Session = Depends(get_db),
        current_user: User = Depends(get_current_user),
        skip: int = 0,
        limit: int = 100,
        order_by: str | None = None,
        order_direction: Literal['asc', 'desc'] = 'asc'
) -> Any:
    organization_setting = await actions.list_organization_setting(
        db=db, skip=skip, limit=limit, order_by=order_by, order_direction=order_direction
    )
    return organization_setting


@organization_settings_router.post(
    "/",
    response_model=schemas.OrganizationSettingsSchema,
    status_code=status.HTTP_201_CREATED,
)
async def create_organization_settings(
        *, db: Session = Depends(get_db),
        current_user: User = Depends(get_current_user),
        organization_settings_in: schemas.OrganizationSettingsCreate
) -> Any:
    organization_settings = await actions.create_organization_settings(db=db,
                                                                       organization_settings_in=organization_settings_in)
    return organization_settings


@organization_settings_router.put(
    "/{id}",
    response_model=schemas.OrganizationSettingsSchema,
    responses={status.HTTP_404_NOT_FOUND: {"model": HTTPError}},
)
async def update_organization_settings(
        *, db: Session = Depends(get_db),
        current_user: User = Depends(get_current_user),
        id: UUID4,
        organization_settings_in: schemas.OrganizationSettingsUpdate,
) -> Any:
    organization_settings = await actions.update_organization_settings(db=db, id=id,
                                                                       organization_settings_in=organization_settings_in)
    return organization_settings


@organization_settings_router.get(
    "/{id}",
    response_model=schemas.OrganizationSettingsSchema,
    responses={status.HTTP_404_NOT_FOUND: {"model": HTTPError}},
)
async def get_organization_settings(
        *, db: Session = Depends(get_db),
        current_user: User = Depends(get_current_user),
        id: UUID4
) -> Any:
    organization_settings = await actions.get_organization_settings(db=db, id=id)
    return organization_settings


@organization_settings_router.delete(
    "/{id}",
    status_code=status.HTTP_204_NO_CONTENT,
    responses={status.HTTP_404_NOT_FOUND: {"model": HTTPError}},
)
async def delete_organization_settings(
        *, db: Session = Depends(get_db),
        current_user: User = Depends(get_current_user),
        id: UUID4
) -> None:
    await actions.delete_organization_settings(db=db, id=id)
