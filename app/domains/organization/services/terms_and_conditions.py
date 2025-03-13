from typing import List, Optional, Literal

from sqlalchemy.orm import Session

from db.base_class import UUID
from domains.organization.repositories.terms_and_conditions import (
    terms_and_conditions as terms_and_conditions_repo
)
from domains.organization.schemas.terms_and_conditions import (
    TermsAndConditionsSchema,
    TermsAndConditionsUpdate,
    TermsAndConditionsCreate, TermsAndConditionsResponse
)


class TermsAndConditionsService:

    def __init__(self):
        self.repo = terms_and_conditions_repo

    async def list_terms_and_condition(
            self, db: Session, *,
            skip: int = 0,
            limit: int = 100,
            order_by: str | None = None,
            order_direction: Literal['asc', 'desc'] = 'asc'
    ) -> List[TermsAndConditionsResponse]:
        terms_and_condition = await terms_and_conditions_repo.get_all(
            db=db, skip=skip, limit=limit,
            order_by=order_by, order_direction=order_direction
        )
        return terms_and_condition

    async def create_terms_and_conditions(self, db: Session, *,
                                          terms_and_conditions_in: TermsAndConditionsCreate) -> TermsAndConditionsSchema:
        terms_and_conditions = await self.repo.create(db=db, data=terms_and_conditions_in)
        return terms_and_conditions

    async def update_terms_and_conditions(self, db: Session, *, id: UUID,
                                          terms_and_conditions_in: TermsAndConditionsUpdate) -> TermsAndConditionsSchema:
        terms_and_conditions = await self.repo.get_by_id(db=db, id=id)
        terms_and_conditions = await self.repo.update(db=db, db_obj=terms_and_conditions,
                                                      data=terms_and_conditions_in)
        return terms_and_conditions

    async def get_terms_and_conditions(self, db: Session, *, id: UUID) -> TermsAndConditionsSchema:
        terms_and_conditions = await self.repo.get_by_id(db=db, id=id)
        return terms_and_conditions

    async def delete_terms_and_conditions(self, db: Session, *, id: UUID) -> None:
        await self.repo.get_by_id(db=db, id=id)
        await self.repo.remove(db=db, id=id)

    async def get_terms_and_conditions_by_keywords(
            self, db: Session, *,
            skip: int = 0,
            limit: int = 100,
            order_by: Optional[str] = None,
            order_direction: Literal['asc', 'desc'] = 'asc',
            **kwargs
    ) -> List[TermsAndConditionsSchema]:
        terms_and_condition = await self.repo.get_by_filters(
            db=db, skip=skip, limit=limit, order_by=order_by, order_direction=order_direction, **kwargs
        )
        return terms_and_condition

    async def search_terms_and_condition(
            self, db: Session, *,
            skip: int = 0,
            limit: int = 100,
            order_by: Optional[str] = None,
            order_direction: Literal['asc', 'desc'] = 'asc',
            **kwargs
    ) -> List[TermsAndConditionsSchema]:
        terms_and_condition = await self.repo.get_by_pattern(
            db=db, skip=skip, limit=limit, order_by=order_by, order_direction=order_direction, **kwargs
        )
        return terms_and_condition


terms_and_conditions_service = TermsAndConditionsService()
