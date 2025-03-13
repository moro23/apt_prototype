from typing import List, Optional, Literal

from sqlalchemy.ext.asyncio import AsyncSession

from db.base_class import UUID
from domains.organization.repositories.bill import bills as bill_repo
from domains.organization.schemas.bill import BillSchema, BillsResponse, BillUpdate, BillCreate


class BillService:

    def __init__(self):
        self.repo = bill_repo

    # service
    async def list_bills(
            self, db: AsyncSession, **params
    ) -> List[BillsResponse]:
        bills = await self.repo.read(params, db)
        # Return only the list of bill records.
        return bills['data']

    async def create_bill(self, db: AsyncSession, *, bill_in: BillCreate) -> BillSchema:
        bill = await self.repo.create(db=db, data=bill_in)
        return bill

    async def update_bill(self, db: AsyncSession, *, id: UUID, bill_in: BillUpdate) -> BillSchema:
        bill = await self.repo.get_by_id(db=db, id=id)
        bill = await self.repo.update(db=db, db_obj=bill, data=bill_in)
        return bill

    async def get_bill(self, db: AsyncSession, *, id: UUID) -> BillSchema:
        bill = await self.repo.get_by_id(db=db, id=id)
        return bill

    async def delete_bill(self, db: AsyncSession, *, id: UUID) -> None:
        await self.repo.get_by_id(db=db, id=id)
        await self.repo.remove(db=db, id=id)

    async def get_bill_by_keywords(
            self, db: AsyncSession, *,
            skip: int = 0,
            limit: int = 100,
            order_by: Optional[str] = None,
            order_direction: Literal['asc', 'desc'] = 'asc',
            **kwargs
    ) -> List[BillSchema]:
        bills = await self.repo.get_by_filters(
            db=db, skip=skip, limit=limit, order_by=order_by, order_direction=order_direction, **kwargs
        )
        return bills

    async def search_bills(
            self, db: AsyncSession, *,
            skip: int = 0,
            limit: int = 100,
            order_by: Optional[str] = None,
            order_direction: Literal['asc', 'desc'] = 'asc',
            **kwargs
    ) -> List[BillSchema]:
        bills = await self.repo.get_by_pattern(
            db=db, skip=skip, limit=limit, order_by=order_by, order_direction=order_direction, **kwargs
        )
        return bills


bill_service = BillService()
