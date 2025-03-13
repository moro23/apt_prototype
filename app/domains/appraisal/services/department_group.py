from typing import List, Any

from domains.appraisal.repositories.department_group import department_group_actions as department_group_repo
from domains.appraisal.schemas.department_group import DepartmentGroupSchema, DepartmentGroupUpdate, \
    DepartmentGroupCreate
from fastapi import HTTPException, status
from pydantic import UUID4
from sqlalchemy.orm import Session


class DepartmentGroupService:

    def __init__(self):
        self.repo = department_group_repo

    async def list_department_groups(self, *, db: Session, skip: int = 0, limit: int = 100) -> List[
        DepartmentGroupSchema]:
        department_groups = await self.repo.get_all(db=db, skip=skip, limit=limit)
        return department_groups

    async def create_department_group(self, *, db: Session,
                                      department_group_in: DepartmentGroupCreate) -> DepartmentGroupSchema:
        department_group = await self.repo.create(db=db, data=department_group_in)
        return department_group

    async def update_department_group(self, *, db: Session, id: UUID4,
                                      department_group_in: DepartmentGroupUpdate) -> DepartmentGroupSchema:
        department_group = await self.repo.get(db=db, id=id)
        if not department_group:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Department group not found")
        department_group = await self.repo.update(db=db, db_obj=department_group, data=department_group_in)
        return department_group

    async def get_department_group(self, *, db: Session, id: UUID4) -> DepartmentGroupSchema:
        department_group = await self.repo.get(db=db, id=id)
        if not department_group:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Department group not found")
        return department_group

    async def delete_department_group(self, *, db: Session, id: UUID4) -> dict[str, Any]:
        department_group = await self.repo.get(db=db, id=id)
        if not department_group:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Department group not found")
        department_group = await self.repo.remove(db=db, id=id)
        return department_group

    async def get_department_group_by_id(self, *, id: UUID4) -> DepartmentGroupSchema:
        department_group = await self.repo.get(id)
        if not department_group:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Department group not found"
            )
        return department_group

    async def get_department_group_by_keywords(self, *, db: Session, tag: str) -> List[DepartmentGroupSchema]:
        pass

    async def search_department_groups(self, *, db: Session, search: str, value: str) -> List[DepartmentGroupSchema]:
        pass

    async def read_by_kwargs(self, *, db: Session, **kwargs) -> Any:
        return await self.repo.get_by_kwargs(self, db, kwargs)


department_group_service = DepartmentGroupService()
