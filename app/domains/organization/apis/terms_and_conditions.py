from typing import Any, Literal

from fastapi import APIRouter, Depends, status
from pydantic import UUID4
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import Session

from db.session import get_db
from domains.auth.models import User
from domains.organization.schemas import terms_and_conditions as schemas
from domains.organization.services.terms_and_conditions import terms_and_conditions_service as actions
from utils.rbac import get_current_user, check_if_is_system_admin
from utils.schemas import HTTPError

terms_and_conditions_router = APIRouter(prefix="/terms_and_condition")


@terms_and_conditions_router.get(
    "/",
    response_model=schemas.TermsAndConditionsResponse,
)
# @ContentQueryChecker(terms_and_conditions.model.c(), None)
async def list_terms_and_condition(
        *, db: AsyncSession = Depends(get_db),
        current_user: User = Depends(check_if_is_system_admin),
        skip: int = 0,
        limit: int = 100,
        order_by: str | None = None,
        order_direction: Literal['asc', 'desc'] = 'asc'
) -> Any:
    terms_and_condition = await actions.list_terms_and_condition(
        db=db, skip=skip, limit=limit, order_by=order_by, order_direction=order_direction
    )
    return terms_and_condition


@terms_and_conditions_router.post(
    "/",
    response_model=schemas.TermsAndConditionsSchema,
    status_code=status.HTTP_201_CREATED,
)
async def create_terms_and_conditions(
        *, db: Session = Depends(get_db),
        current_user: User = Depends(get_current_user),
        terms_and_conditions_in: schemas.TermsAndConditionsCreate
) -> Any:
    terms_and_conditions = await actions.create_terms_and_conditions(db=db,
                                                                     terms_and_conditions_in=terms_and_conditions_in)
    return terms_and_conditions


@terms_and_conditions_router.put(
    "/{id}",
    response_model=schemas.TermsAndConditionsSchema,
    responses={status.HTTP_404_NOT_FOUND: {"model": HTTPError}},
)
async def update_terms_and_conditions(
        *, db: Session = Depends(get_db),
        current_user: User = Depends(get_current_user),
        id: UUID4,
        terms_and_conditions_in: schemas.TermsAndConditionsUpdate,
) -> Any:
    terms_and_conditions = await actions.update_terms_and_conditions(db=db, id=id,
                                                                     terms_and_conditions_in=terms_and_conditions_in)
    return terms_and_conditions


@terms_and_conditions_router.get(
    "/{id}",
    response_model=schemas.TermsAndConditionsSchema,
    responses={status.HTTP_404_NOT_FOUND: {"model": HTTPError}},
)
async def get_terms_and_conditions(
        *, db: Session = Depends(get_db),
        current_user: User = Depends(get_current_user),
        id: UUID4
) -> Any:
    terms_and_conditions = await actions.get_terms_and_conditions(db=db, id=id)
    return terms_and_conditions


@terms_and_conditions_router.delete(
    "/{id}",
    status_code=status.HTTP_204_NO_CONTENT,
    responses={status.HTTP_404_NOT_FOUND: {"model": HTTPError}},
)
async def delete_terms_and_conditions(
        *, db: Session = Depends(get_db),
        current_user: User = Depends(get_current_user),
        id: UUID4
) -> None:
    await actions.delete_terms_and_conditions(db=db, id=id)
