from typing import Any, List, Literal

from fastapi import APIRouter, Depends, status
from pydantic import UUID4
from sqlalchemy.orm import Session

from db.session import get_db
from domains.auth.models import User
from domains.organization.schemas import organization_branch as schemas
from domains.organization.services.organization_branch import organization_branch_service as actions
from utils.rbac import get_current_user
from utils.schemas import HTTPError

organization_branch_router = APIRouter(prefix="/branches")


@organization_branch_router.get(
    "/",
    response_model=List[schemas.OrganizationBranchSchema],
)
async def list_organization_branches(
        *, db: Session = Depends(get_db),
        current_user: User = Depends(get_current_user),
        skip: int = 0,
        limit: int = 100,
        order_by: str | None = None,
        order_direction: Literal['asc', 'desc'] = 'asc'
) -> Any:
    organization_branches = await actions.list_organization_branches(
        db=db, skip=skip, limit=limit, order_by=order_by, order_direction=order_direction
    )
    return organization_branches


@organization_branch_router.post(
    "/",
    response_model=schemas.OrganizationBranchSchema,
    status_code=status.HTTP_201_CREATED,
)
async def create_organization_branch(
        *, db: Session = Depends(get_db),
        current_user: User = Depends(get_current_user),
        organization_branch_in: schemas.OrganizationBranchCreate
) -> Any:
    organization_branch = await actions.create_organization_branch(db=db, organization_branch_in=organization_branch_in)
    return organization_branch


@organization_branch_router.put(
    "/{id}",
    response_model=schemas.OrganizationBranchSchema,
    responses={status.HTTP_404_NOT_FOUND: {"model": HTTPError}},
)
async def update_organization_branch(
        *, db: Session = Depends(get_db),
        current_user: User = Depends(get_current_user),
        id: UUID4,
        organization_branch_in: schemas.OrganizationBranchUpdate,
) -> Any:
    organization_branch = await actions.update_organization_branch(db=db, id=id,
                                                                   organization_branch_in=organization_branch_in)
    return organization_branch


@organization_branch_router.get(
    "/{id}",
    response_model=schemas.OrganizationBranchSchema,
    responses={status.HTTP_404_NOT_FOUND: {"model": HTTPError}},
)
async def get_organization_branch(
        *, db: Session = Depends(get_db),
        current_user: User = Depends(get_current_user),
        id: UUID4
) -> Any:
    organization_branch = await actions.get_organization_branch(db=db, id=id)
    return organization_branch


@organization_branch_router.delete(
    "/{id}",
    status_code=status.HTTP_204_NO_CONTENT,
    responses={status.HTTP_404_NOT_FOUND: {"model": HTTPError}},
)
async def delete_organization_branch(
        *, db: Session = Depends(get_db),
        current_user: User = Depends(get_current_user),
        id: UUID4
) -> None:
    await actions.delete_organization_branch(db=db, id=id)
