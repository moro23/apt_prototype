from typing import List, Optional, Literal

from sqlalchemy.orm import Session

from db.base_class import UUID
from domains.staff.repositories.staff import staff_actions as staff_repo
from domains.staff.schemas.staff import StaffSchema, StaffUpdate, StaffCreate


class StaffService:

    def __init__(self):
        self.repo = staff_repo

    def list_staffs(
            self, db: Session, *,
            skip: int = 0,
            limit: int = 100,
            order_by: str | None = None,
            order_direction: Literal['asc', 'desc'] = 'asc'
    ) -> List[StaffSchema]:
        staffs = self.repo.get_all(
            db=db, skip=skip, limit=limit, order_by=order_by, order_direction=order_direction
        )
        return staffs

    def create_staff(self, db: Session, *, staff_in: StaffCreate) -> StaffSchema:
        staff = self.repo.create(db=db, data=staff_in)
        return staff

    def update_staff(self, db: Session, *, id: UUID, staff_in: StaffUpdate) -> StaffSchema:
        staff = self.repo.get_by_id(db=db, id=id)
        staff = self.repo.update(db=db, db_obj=staff, data=staff_in)
        return staff

    def get_staff(self, db: Session, *, id: UUID) -> StaffSchema:
        staff = self.repo.get_by_id(db=db, id=id)
        return staff

    def delete_staff(self, db: Session, *, id: UUID) -> StaffSchema:
        self.repo.get_by_id(db=db, id=id)
        self.repo.remove(db=db, id=id)

    def get_staff_by_keywords(
            self, db: Session, *,
            skip: int = 0,
            limit: int = 100,
            order_by: Optional[str] = None,
            order_direction: Literal['asc', 'desc'] = 'asc',
            **kwargs
    ) -> List[StaffSchema]:
        staffs = self.repo.get_by_filters(
            db=db, skip=skip, limit=limit, order_by=order_by, order_direction=order_direction, **kwargs
        )
        return staffs

    def search_staffs(
            self, db: Session, *,
            skip: int = 0,
            limit: int = 100,
            order_by: Optional[str] = None,
            order_direction: Literal['asc', 'desc'] = 'asc',
            **kwargs
    ) -> List[StaffSchema]:
        staffs = self.repo.get_by_pattern(
            db=db, skip=skip, limit=limit, order_by=order_by, order_direction=order_direction, **kwargs
        )
        return staffs


staff_service = StaffService()
