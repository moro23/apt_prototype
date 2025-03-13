from typing import List, Optional, Literal

from sqlalchemy.orm import Session

from db.base_class import UUID
from domains.organization.repositories.payment import payment_actions as payment_repo
from domains.organization.schemas.payment import PaymentSchema, PaymentUpdate, PaymentCreate


class PaymentService:

    def __init__(self):
        self.repo = payment_repo

    async def list_payments(
            self, db: Session, *,
            skip: int = 0,
            limit: int = 100,
            order_by: str | None = None,
            order_direction: Literal['asc', 'desc'] = 'asc'
    ) -> List[PaymentSchema]:
        payments = await self.repo.get_all(
            db=db, skip=skip, limit=limit, order_by=order_by, order_direction=order_direction
        )
        return payments

    async def create_payment(self, db: Session, *, payment_in: PaymentCreate) -> PaymentSchema:
        payment = await self.repo.create(db=db, data=payment_in)
        return payment

    async def update_payment(self, db: Session, *, id: UUID, payment_in: PaymentUpdate) -> PaymentSchema:
        payment = await self.repo.get_by_id(db=db, id=id)
        payment = await self.repo.update(db=db, db_obj=payment, data=payment_in)
        return payment

    async def get_payment(self, db: Session, *, id: UUID) -> PaymentSchema:
        payment = await self.repo.get_by_id(db=db, id=id)
        return payment

    async def delete_payment(self, db: Session, *, id: UUID) -> None:
        await self.repo.get_by_id(db=db, id=id)
        await self.repo.remove(db=db, id=id)

    async def get_payment_by_keywords(
            self, db: Session, *,
            skip: int = 0,
            limit: int = 100,
            order_by: Optional[str] = None,
            order_direction: Literal['asc', 'desc'] = 'asc',
            **kwargs
    ) -> List[PaymentSchema]:
        payments = await self.repo.get_by_filters(
            db=db, skip=skip, limit=limit, order_by=order_by, order_direction=order_direction, **kwargs
        )
        return payments

    async def search_payments(
            self, db: Session, *,
            skip: int = 0,
            limit: int = 100,
            order_by: Optional[str] = None,
            order_direction: Literal['asc', 'desc'] = 'asc',
            **kwargs
    ) -> List[PaymentSchema]:
        payments = await self.repo.get_by_pattern(
            db=db, skip=skip, limit=limit, order_by=order_by, order_direction=order_direction, **kwargs
        )
        return payments


payment_service = PaymentService()
