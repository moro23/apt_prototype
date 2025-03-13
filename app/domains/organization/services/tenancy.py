from typing import List, Optional, Literal

from sqlalchemy.orm import Session

from db.base_class import UUID
from domains.organization.repositories.tenancy import tenancy_actions as tenancy_repo
from domains.organization.schemas.tenancy import TenancySchema, TenancyUpdate, TenancyCreate


class TenancyService:

    def __init__(self):
        self.repo = tenancy_repo

    async def list_tenancies(
            self, db: Session, *,
            skip: int = 0,
            limit: int = 100,
            order_by: str | None = None,
            order_direction: Literal['asc', 'desc'] = 'asc'
    ) -> List[TenancySchema]:
        tenancies = await self.repo.get_all(
            db=db, skip=skip, limit=limit, order_by=order_by, order_direction=order_direction
        )
        return tenancies

    async def create_tenancy(self, db: Session, *, tenancy_in: TenancyCreate) -> TenancySchema:
        tenancy = await self.repo.create(db=db, data=tenancy_in)
        return tenancy

    async def update_tenancy(self, db: Session, *, id: UUID, tenancy_in: TenancyUpdate) -> TenancySchema:
        tenancy = await self.repo.get_by_id(db=db, id=id)
        tenancy = await self.repo.update(db=db, db_obj=tenancy, data=tenancy_in)
        return tenancy

    async def get_tenancy(self, db: Session, *, id: UUID) -> TenancySchema:
        tenancy = await self.repo.get_by_id(db=db, id=id)
        return tenancy

    async def delete_tenancy(self, db: Session, *, id: UUID) -> None:
        await self.repo.get_by_id(db=db, id=id)
        await self.repo.remove(db=db, id=id)

    async def get_tenancy_by_keywords(
            self, db: Session, *,
            skip: int = 0,
            limit: int = 100,
            order_by: Optional[str] = None,
            order_direction: Literal['asc', 'desc'] = 'asc',
            **kwargs
    ) -> List[TenancySchema]:
        tenancies = await self.repo.get_by_filters(
            db=db, skip=skip, limit=limit, order_by=order_by, order_direction=order_direction, **kwargs
        )
        return tenancies

    async def search_tenancies(
            self, db: Session, *,
            skip: int = 0,
            limit: int = 100,
            order_by: Optional[str] = None,
            order_direction: Literal['asc', 'desc'] = 'asc',
            **kwargs
    ) -> List[TenancySchema]:
        tenancies = await self.repo.get_by_pattern(
            db=db, skip=skip, limit=limit, order_by=order_by, order_direction=order_direction, **kwargs
        )
        return tenancies


tenancy_service = TenancyService()
