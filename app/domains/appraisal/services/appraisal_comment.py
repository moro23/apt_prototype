from typing import List, Optional, Literal

from sqlalchemy.orm import Session

from db.base_class import UUID
from domains.appraisal.repositories.appraisal_comment import appraisal_comment_actions as appraisal_comment_repo
from domains.appraisal.schemas.appraisal_comment import (
    AppraisalCommentSchema,
    AppraisalCommentUpdate,
    AppraisalCommentCreate
)


class AppraisalCommentService:

    def __init__(self):
        self.repo = appraisal_comment_repo

    def list_appraisal_comments(
            self, db: Session, *,
            skip: int = 0,
            limit: int = 100,
            order_by: str | None = None,
            order_direction: Literal['asc', 'desc'] = 'asc'
    ) -> List[AppraisalCommentSchema]:
        appraisal_comments = self.repo.get_all(
            db=db, skip=skip, limit=limit, order_by=order_by, order_direction=order_direction
        )
        return appraisal_comments

    def create_appraisal_comment(self, db: Session, *,
                                 appraisal_comment_in: AppraisalCommentCreate) -> AppraisalCommentSchema:
        appraisal_comment = self.repo.create(db=db, data=appraisal_comment_in)
        return appraisal_comment

    def update_appraisal_comment(self, db: Session, *, id: UUID,
                                 appraisal_comment_in: AppraisalCommentUpdate) -> AppraisalCommentSchema:
        appraisal_comment = self.repo.get_by_id(db=db, id=id)
        appraisal_comment = self.repo.update(db=db, db_obj=appraisal_comment, data=appraisal_comment_in)
        return appraisal_comment

    def get_appraisal_comment(self, db: Session, *, id: UUID) -> AppraisalCommentSchema:
        appraisal_comment = self.repo.get_by_id(db=db, id=id)
        return appraisal_comment

    def delete_appraisal_comment(self, db: Session, *, id: UUID) -> AppraisalCommentSchema:
        appraisal_comment = self.repo.get_by_id(db=db, id=id)
        appraisal_comment = self.repo.remove(db=db, id=id)
        return appraisal_comment

    def get_appraisal_comment_by_keywords(
            self, db: Session, *,
            skip: int = 0,
            limit: int = 100,
            order_by: Optional[str] = None,
            order_direction: Literal['asc', 'desc'] = 'asc',
            **kwargs
    ) -> List[AppraisalCommentSchema]:
        appraisal_comments = self.repo.get_by_filters(
            db=db, skip=skip, limit=limit, order_by=order_by, order_direction=order_direction, **kwargs
        )
        return appraisal_comments

    def search_appraisal_comments(
            self, db: Session, *,
            skip: int = 0,
            limit: int = 100,
            order_by: Optional[str] = None,
            order_direction: Literal['asc', 'desc'] = 'asc',
            **kwargs
    ) -> List[AppraisalCommentSchema]:
        appraisal_comments = self.repo.get_by_pattern(
            db=db, skip=skip, limit=limit, order_by=order_by, order_direction=order_direction, **kwargs
        )
        return appraisal_comments


appraisal_comment_service = AppraisalCommentService()
