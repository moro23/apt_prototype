from typing import Any, List, Literal

from fastapi import APIRouter, Depends
from pydantic import UUID4
from sqlalchemy.orm import Session
from starlette.status import HTTP_201_CREATED, HTTP_404_NOT_FOUND

from db.session import get_db
from domains.appraisal.schemas import appraisal_comment as schemas
from domains.appraisal.services.appraisal_comment import appraisal_comment_service as actions
from domains.auth.models import User
from utils.rbac import get_current_user
from utils.schemas import HTTPError

appraisal_comment_router = APIRouter(prefix='/comments')


@appraisal_comment_router.get(
    "/",
    response_model=List[schemas.AppraisalCommentSchema],
)
def list_appraisal_comments(
        *, db: Session = Depends(get_db),
        current_user: User = Depends(get_current_user),
        skip: int = 0,
        limit: int = 100,
        order_by: str | None = None,
        order_direction: Literal['asc', 'desc'] = 'asc'
) -> Any:
    appraisal_comments = actions.list_appraisal_comments(
        db=db, skip=skip, limit=limit, order_by=order_by, order_direction=order_direction
    )
    return appraisal_comments


@appraisal_comment_router.post(
    "/",
    response_model=schemas.AppraisalCommentSchema,
    status_code=HTTP_201_CREATED,
)
def create_appraisal_comment(
        *, db: Session = Depends(get_db),
        current_user: User = Depends(get_current_user),
        appraisal_comment_in: schemas.AppraisalCommentCreate
) -> Any:
    appraisal_comment = actions.create_appraisal_comment(db=db, appraisal_comment_in=appraisal_comment_in)
    return appraisal_comment


@appraisal_comment_router.put(
    "/{id}",
    response_model=schemas.AppraisalCommentSchema,
    responses={HTTP_404_NOT_FOUND: {"model": HTTPError}},
)
def update_appraisal_comment(
        *, db: Session = Depends(get_db),
        current_user: User = Depends(get_current_user),
        id: UUID4,
        appraisal_comment_in: schemas.AppraisalCommentUpdate,
) -> Any:
    appraisal_comment = actions.update_appraisal_comment(db=db, id=id, appraisal_comment_in=appraisal_comment_in)
    return appraisal_comment


@appraisal_comment_router.get(
    "/{id}",
    response_model=schemas.AppraisalCommentSchema,
    responses={HTTP_404_NOT_FOUND: {"model": HTTPError}},
)
def get_appraisal_comment(
        *, db: Session = Depends(get_db),
        current_user: User = Depends(get_current_user),
        id: UUID4
) -> Any:
    appraisal_comment = actions.get_appraisal_comment(db=db, id=id)
    return appraisal_comment


@appraisal_comment_router.delete(
    "/{id}",
    response_model=schemas.AppraisalCommentSchema,
    responses={HTTP_404_NOT_FOUND: {"model": HTTPError}},
)
def delete_appraisal_comment(
        *, db: Session = Depends(get_db),
        current_user: User = Depends(get_current_user),
        id: UUID4
) -> Any:
    appraisal_comment = actions.delete_appraisal_comment(db=db, id=id)
    return appraisal_comment
