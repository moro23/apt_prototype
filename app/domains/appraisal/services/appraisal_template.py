from typing import List, Optional, Literal

from domains.appraisal.repositories.appraisal_template import appraisal_template_actions as appraisal_template_repo
from domains.appraisal.schemas.appraisal_template import AppraisalTemplateSchema, AppraisalTemplateUpdate, \
    AppraisalTemplateCreate
from sqlalchemy.orm import Session

from db.base_class import UUID


class AppraisalTemplateService:

    def __init__(self):
        self.repo = appraisal_template_repo

    def list_appraisal_templates(
            self, db: Session, *,
            skip: int = 0,
            limit: int = 100,
            order_by: str | None = None,
            order_direction: Literal['asc', 'desc'] = 'asc'
    ) -> List[AppraisalTemplateSchema]:
        appraisal_templates = self.repo.get_all(
            db=db, skip=skip, limit=limit, order_by=order_by, order_direction=order_direction
        )
        return appraisal_templates

    def create_appraisal_template(self, db: Session, *,
                                  appraisal_template_in: AppraisalTemplateCreate) -> AppraisalTemplateSchema:
        appraisal_template = self.repo.create(db=db, data=appraisal_template_in)
        return appraisal_template

    def update_appraisal_template(self, db: Session, *, id: UUID,
                                  appraisal_template_in: AppraisalTemplateUpdate) -> AppraisalTemplateSchema:
        appraisal_template = self.repo.get_by_id(db=db, id=id)
        appraisal_template = self.repo.update(db=db, db_obj=appraisal_template, data=appraisal_template_in)
        return appraisal_template

    def get_appraisal_template(self, db: Session, *, id: UUID) -> AppraisalTemplateSchema:
        appraisal_template = self.repo.get_by_id(db=db, id=id)
        return appraisal_template

    def delete_appraisal_template(self, db: Session, *, id: UUID) -> AppraisalTemplateSchema:
        appraisal_template = self.repo.get_by_id(db=db, id=id)
        appraisal_template = self.repo.remove(db=db, id=id)
        return appraisal_template

    def get_appraisal_template_by_keywords(
            self, db: Session, *,
            skip: int = 0,
            limit: int = 100,
            order_by: Optional[str] = None,
            order_direction: Literal['asc', 'desc'] = 'asc',
            **kwargs
    ) -> List[AppraisalTemplateSchema]:
        appraisal_templates = self.repo.get_by_filters(
            db=db, skip=skip, limit=limit, order_by=order_by, order_direction=order_direction, **kwargs
        )
        return appraisal_templates

    def search_appraisal_templates(
            self, db: Session, *,
            skip: int = 0,
            limit: int = 100,
            order_by: Optional[str] = None,
            order_direction: Literal['asc', 'desc'] = 'asc',
            **kwargs
    ) -> List[AppraisalTemplateSchema]:
        appraisal_templates = self.repo.get_by_pattern(
            db=db, skip=skip, limit=limit, order_by=order_by, order_direction=order_direction, **kwargs
        )
        return appraisal_templates


appraisal_template_service = AppraisalTemplateService()
