from typing import Any, List, Literal

from fastapi import APIRouter, Depends, status
from pydantic import UUID4
from sqlalchemy.orm import Session

from db.session import get_db
from domains.auth.models import User
from domains.organization.schemas import form_template as schemas
from domains.organization.services.form_template import form_field_template_service as actions
from utils.rbac import get_current_user
from utils.schemas import HTTPError

form_field_template_router = APIRouter(prefix="/form_field_templates", tags=["FORMFIELDTEMPLATE"])


@form_field_template_router.get(
    "/",
    response_model=List[schemas.FormFieldTemplateSchema],
)
async def list_form_field_templates(
        *, db: Session = Depends(get_db),
        current_user: User = Depends(get_current_user),
        skip: int = 0,
        limit: int = 100,
        order_by: str | None = None,
        order_direction: Literal['asc', 'desc'] = 'asc'
) -> Any:
    form_field_templates = await actions.list_form_field_templates(
        db=db, skip=skip, limit=limit, order_by=order_by, order_direction=order_direction
    )
    return form_field_templates


@form_field_template_router.post(
    "/",
    response_model=schemas.FormFieldTemplateSchema,
    status_code=status.HTTP_201_CREATED,
)
async def create_form_field_template(
        *, db: Session = Depends(get_db),
        current_user: User = Depends(get_current_user),
        form_field_template_in: schemas.FormFieldTemplateCreate
) -> Any:
    form_field_template = await actions.create_form_field_template(db=db, form_field_template_in=form_field_template_in)
    return form_field_template


@form_field_template_router.put(
    "/{id}",
    response_model=schemas.FormFieldTemplateSchema,
    responses={status.HTTP_404_NOT_FOUND: {"model": HTTPError}},
)
async def update_form_field_template(
        *, db: Session = Depends(get_db),
        current_user: User = Depends(get_current_user),
        id: UUID4,
        form_field_template_in: schemas.FormFieldTemplateUpdate,
) -> Any:
    form_field_template = await actions.update_form_field_template(db=db, id=id,
                                                                   form_field_template_in=form_field_template_in)
    return form_field_template


@form_field_template_router.get(
    "/{id}",
    response_model=schemas.FormFieldTemplateSchema,
    responses={status.HTTP_404_NOT_FOUND: {"model": HTTPError}},
)
async def get_form_field_template(
        *, db: Session = Depends(get_db),
        current_user: User = Depends(get_current_user),
        id: UUID4
) -> Any:
    form_field_template = await actions.get_form_field_template(db=db, id=id)
    return form_field_template


@form_field_template_router.delete(
    "/{id}",
    status_code=status.HTTP_204_NO_CONTENT,
    responses={status.HTTP_404_NOT_FOUND: {"model": HTTPError}},
)
async def delete_form_field_template(
        *, db: Session = Depends(get_db),
        current_user: User = Depends(get_current_user),
        id: UUID4
) -> None:
    await actions.delete_form_field_template(db=db, id=id)
