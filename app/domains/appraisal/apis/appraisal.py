from datetime import datetime
from typing import Any, List

from fastapi import APIRouter, Depends
from fastapi import HTTPException
from pydantic import UUID4
from sqlalchemy.orm import Session
from starlette.status import HTTP_201_CREATED, HTTP_404_NOT_FOUND

from db.session import get_db
from domains.appraisal.schemas import appraisal as schemas
from domains.appraisal.services.appraisal import appraisal_service as actions
from domains.auth.models.users import User
from utils.rbac import get_current_user
from utils.schemas import HTTPError

appraisal_router = APIRouter()


@appraisal_router.get(
    "/",
    response_model=List[schemas.AppraisalSchema]
)
async def list_appraisals(
        db: Session = Depends(get_db),
        current_user: User = Depends(get_current_user),
        skip: int = 0,
        limit: int = 100,
        date_from: datetime = None,
        date_to: datetime = None,
) -> Any:
    appraisals = actions.list_appraisals(
        db=db, skip=skip, limit=limit, date_from=date_from, date_to=date_to
    )
    return appraisals


@appraisal_router.post(
    "/",
    response_model=schemas.AppraisalSchema,
    status_code=HTTP_201_CREATED
)
async def create_appraisal(
        *, db: Session = Depends(get_db),
        current_user: User = Depends(get_current_user),
        appraisal_in: schemas.AppraisalCreate
) -> Any:
    appraisal = actions.create_appraisal(db=db, appraisal_in=appraisal_in)
    return appraisal


@appraisal_router.put(
    "/{id}",
    response_model=schemas.AppraisalSchema,
    responses={HTTP_404_NOT_FOUND: {"model": HTTPError}}
)
async def update_appraisal(
        *, db: Session = Depends(get_db),
        current_user: User = Depends(get_current_user),
        id: UUID4,
        appraisal_in: schemas.AppraisalUpdate,
) -> Any:
    appraisal = actions.get_appraisal(db=db, id=id)
    if not appraisal:
        raise HTTPException(
            status_code=HTTP_404_NOT_FOUND,
            detail="Appraisal not found"
        )
    appraisal = actions.update_appraisal(db=db, id=appraisal.id, appraisal_in=appraisal_in)
    return appraisal


@appraisal_router.get(
    "/{id}",
    response_model=schemas.SingleAppraisalSchema,
    responses={HTTP_404_NOT_FOUND: {"model": HTTPError}}
)
async def get_appraisal(
        *, db: Session = Depends(get_db),
        current_user: User = Depends(get_current_user),
        id: UUID4
) -> Any:
    appraisal = actions.get_appraisal(db=db, id=id)
    if not appraisal:
        raise HTTPException(
            status_code=HTTP_404_NOT_FOUND,
            detail="Appraisal not found"
        )
    return appraisal


@appraisal_router.delete(
    "/{id}",
    response_model=dict[str, Any],
    responses={HTTP_404_NOT_FOUND: {"model": HTTPError}}
)
async def delete_appraisal(
        *, db: Session = Depends(get_db),
        current_user: User = Depends(get_current_user),
        id: UUID4
) -> Any:
    appraisal = actions.get_appraisal(db=db, id=id)
    if not appraisal:
        raise HTTPException(
            status_code=HTTP_404_NOT_FOUND,
            detail="Appraisal not found"
        )
    appraisal = actions.delete_appraisal(db=db, id=id)
    return appraisal
