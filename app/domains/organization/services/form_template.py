from typing import List, Optional, Literal

from sqlalchemy.orm import Session

from db.base_class import UUID
from domains.organization.repositories.form_template import form_field_template_actions as form_field_template_repo
from domains.organization.schemas.form_template import (
    FormFieldTemplateSchema,
    FormFieldTemplateUpdate,
    FormFieldTemplateCreate
)


class FormFieldTemplateService:

    def __init__(self):
        self.repo = form_field_template_repo

    async def list_form_field_templates(
            self, db: Session, *,
            skip: int = 0,
            limit: int = 100,
            order_by: str | None = None,
            order_direction: Literal['asc', 'desc'] = 'asc'
    ) -> List[FormFieldTemplateSchema]:
        form_field_templates = await self.repo.get_all(
            db=db, skip=skip, limit=limit, order_by=order_by, order_direction=order_direction
        )
        return form_field_templates

    async def create_form_field_template(
            self, db: Session, *, form_field_template_in: FormFieldTemplateCreate
    ) -> FormFieldTemplateSchema:
        form_field_template = await self.repo.create(db=db, data=form_field_template_in)
        return form_field_template

    async def update_form_field_template(
            self, db: Session, *, id: UUID, form_field_template_in: FormFieldTemplateUpdate
    ) -> FormFieldTemplateSchema:
        form_field_template = await self.repo.get_by_id(db=db, id=id)
        form_field_template = await self.repo.update(db=db, db_obj=form_field_template, data=form_field_template_in)
        return form_field_template

    async def get_form_field_template(self, db: Session, *, id: UUID) -> FormFieldTemplateSchema:
        form_field_template = await self.repo.get_by_id(db=db, id=id)
        return form_field_template

    async def delete_form_field_template(self, db: Session, *, id: UUID) -> None:
        form_field_template = await self.repo.get_by_id(db=db, id=id)
        await self.repo.remove(db=db, id=id)

    async def get_form_field_template_by_keywords(
            self, db: Session, *,
            skip: int = 0,
            limit: int = 100,
            order_by: Optional[str] = None,
            order_direction: Literal['asc', 'desc'] = 'asc',
            **kwargs
    ) -> List[FormFieldTemplateSchema]:
        form_field_templates = await self.repo.get_by_filters(
            db=db, skip=skip, limit=limit, order_by=order_by, order_direction=order_direction, **kwargs
        )
        return form_field_templates

    async def search_form_field_templates(
            self, db: Session, *,
            skip: int = 0,
            limit: int = 100,
            order_by: Optional[str] = None,
            order_direction: Literal['asc', 'desc'] = 'asc',
            **kwargs
    ) -> List[FormFieldTemplateSchema]:
        form_field_templates = await self.repo.get_by_pattern(
            db=db, skip=skip, limit=limit, order_by=order_by, order_direction=order_direction, **kwargs
        )
        return form_field_templates


form_field_template_service = FormFieldTemplateService()
