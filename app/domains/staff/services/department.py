from typing import List, Optional, Literal

from sqlalchemy.orm import Session

from db.base_class import UUID
from domains.staff.repositories.department import department_actions as department_repo
from domains.staff.schemas.department import DepartmentSchema, DepartmentUpdate, DepartmentCreate


class DepartmentService:

    def __init__(self):
        self.repo = department_repo

    def list_departments(
            self, db: Session, *,
            skip: int = 0,
            limit: int = 100,
            order_by: str | None = None,
            order_direction: Literal['asc', 'desc'] = 'asc'
    ) -> List[DepartmentSchema]:
        departments = self.repo.get_all(
            db=db, skip=skip, limit=limit, order_by=order_by, order_direction=order_direction
        )
        return departments

    def create_department(self, db: Session, *, department_in: DepartmentCreate) -> DepartmentSchema:
        department = self.repo.create(db=db, data=department_in)
        return department

    def update_department(self, db: Session, *, id: UUID, department_in: DepartmentUpdate) -> DepartmentSchema:
        department = self.repo.update(db=db, id=id, data=department_in)
        return department

    def get_department(self, db: Session, *, id: UUID) -> DepartmentSchema:
        department = self.repo.get_by_id(db=db, id=id)
        return department

    def delete_department(self, db: Session, *, id: UUID) -> DepartmentSchema:
        self.repo.get_by_id(db=db, id=id)
        self.repo.remove(db=db, id=id)

    def get_department_by_keywords(
            self, db: Session, *,
            skip: int = 0,
            limit: int = 100,
            order_by: Optional[str] = None,
            order_direction: Literal['asc', 'desc'] = 'asc',
            **kwargs
    ) -> List[DepartmentSchema]:
        departments = self.repo.get_by_filters(
            db=db, skip=skip, limit=limit, order_by=order_by, order_direction=order_direction, **kwargs
        )
        return departments

    def search_departments(
            self, db: Session, *,
            skip: int = 0,
            limit: int = 100,
            order_by: Optional[str] = None,
            order_direction: Literal['asc', 'desc'] = 'asc',
            **kwargs
    ) -> List[DepartmentSchema]:
        departments = self.repo.get_by_pattern(
            db=db, skip=skip, limit=limit, order_by=order_by, order_direction=order_direction, **kwargs
        )
        return departments


department_service = DepartmentService()
