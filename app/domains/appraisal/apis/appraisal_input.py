from datetime import datetime
from typing import Any, List, Optional

from db.session import get_db
from domains.appraisal.schemas import appraisal_input as schemas
from domains.appraisal.services.appraisal_input import appraisal_input_service as actions
from domains.auth.models.users import User
from fastapi import APIRouter, Depends
from fastapi import HTTPException
from pydantic import UUID4
from sqlalchemy.orm import Session
from starlette.status import HTTP_201_CREATED, HTTP_404_NOT_FOUND
from utils.rbac import get_current_user
from utils.schemas import HTTPError

appraisal_input_router = APIRouter(prefix='/inputs')


@appraisal_input_router.get(
    "/",
    response_model=List[schemas.AppraisalInputSchema],

)
async def list_appraisal_inputs(
        db: Session = Depends(get_db),
        current_user: User = Depends(get_current_user),
        skip: int = 0,
        limit: int = 100,
        appraisal_id: Optional[UUID4] = None,
        staff_id: Optional[UUID4] = None,
        appraisal_year: Optional[int] = None,
        cycle: Optional[str] = None,
        department_id: Optional[UUID4] = None,
        is_global: Optional[bool] = None,
        is_active: Optional[bool] = None,
        date_from: datetime = None,
        date_to: datetime = None,
) -> Any:
    appraisal_inputs = actions.list_appraisal_inputs(
        db=db, skip=skip, limit=limit,
        appraisal_id=appraisal_id,
        staff_id=staff_id,
        appraisal_year=appraisal_year,
        cycle=cycle,
        department_id=department_id,
        is_global=is_global,
        is_active=is_active,
        date_from=date_from,
        date_to=date_to,
    )
    return appraisal_inputs


@appraisal_input_router.post(
    "/",
    response_model=schemas.AppraisalInputSchema,
    status_code=HTTP_201_CREATED,

)
async def create_appraisal_input(
        *, db: Session = Depends(get_db),
        current_user: User = Depends(get_current_user),
        appraisal_input_in: schemas.AppraisalInputCreate
) -> Any:
    appraisal_input = actions.create_appraisal_input(db=db, appraisal_input_in=appraisal_input_in)
    return appraisal_input


@appraisal_input_router.put(
    "/{id}",
    response_model=schemas.AppraisalInputSchema,
    responses={HTTP_404_NOT_FOUND: {"model": HTTPError}},

)
async def update_appraisal_input(
        *, db: Session = Depends(get_db),
        current_user: User = Depends(get_current_user),
        id: UUID4,
        appraisal_input_in: schemas.AppraisalInputUpdate,
) -> Any:
    appraisal_input = actions.get_appraisal_input(db=db, id=id)
    if not appraisal_input:
        raise HTTPException(
            status_code=HTTP_404_NOT_FOUND,
            detail="Appraisal input not found"
        )
    appraisal_input = actions.update_appraisal_input(
        db=db, id=appraisal_input.id, appraisal_input_in=appraisal_input_in
    )
    return appraisal_input


@appraisal_input_router.get(
    "/{id}",
    response_model=schemas.AppraisalInputSchema,
    responses={HTTP_404_NOT_FOUND: {"model": HTTPError}},

)
async def get_appraisal_input(
        *, db: Session = Depends(get_db),
        current_user: User = Depends(get_current_user),
        id: UUID4
) -> Any:
    appraisal_input = actions.get_appraisal_input(db=db, id=id)
    if not appraisal_input:
        raise HTTPException(
            status_code=HTTP_404_NOT_FOUND,
            detail="Appraisal input not found"
        )
    return appraisal_input


@appraisal_input_router.delete(
    "/{id}",
    response_model=dict[str, Any],
    responses={HTTP_404_NOT_FOUND: {"model": HTTPError}},

)
async def delete_appraisal_input(
        *, db: Session = Depends(get_db),
        current_user: User = Depends(get_current_user),
        id: UUID4
) -> Any:
    appraisal_input = actions.get_appraisal_input(db=db, id=id)
    if not appraisal_input:
        raise HTTPException(
            status_code=HTTP_404_NOT_FOUND,
            detail="Appraisal input not found"
        )
    appraisal_input = actions.delete_appraisal_input(db=db, id=id)
    return appraisal_input
