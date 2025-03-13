from datetime import datetime
from typing import List, Any

from domains.appraisal.repositories.appraisal import appraisal_actions as appraisal_repo
from domains.appraisal.schemas.appraisal import AppraisalSchema, AppraisalUpdate, AppraisalCreate
from fastapi import HTTPException, status
from pydantic import UUID4
from sqlalchemy.orm import Session


class AppraisalService:

    def __init__(self):
        self.repo = appraisal_repo

    async def list_appraisals(
            self, *, db: Session, skip: int = 0, limit: int = 100,
            date_from: datetime = None,
            date_to: datetime = None,
    ) -> List[AppraisalSchema]:
        appraisals = await self.repo.get_all(
            db=db, skip=skip, limit=limit, date_from=date_from, date_to=date_to
        )
        return appraisals

    async def create_appraisal(self, *, db: Session, appraisal_in: AppraisalCreate) -> AppraisalSchema:
        appraisal = await self.repo.create(db=db, data=appraisal_in)
        return appraisal

    async def update_appraisal(self, *, db: Session, id: UUID4, appraisal_in: AppraisalUpdate) -> AppraisalSchema:
        appraisal = await self.repo.get(db=db, id=id)
        if not appraisal:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Appraisal not found")
        appraisal = await self.repo.update(db=db, db_obj=appraisal, data=appraisal_in)
        return appraisal

    async def get_appraisal(self, *, db: Session, id: UUID4) -> AppraisalSchema:
        appraisal = await self.repo.get(db=db, id=id)
        if not appraisal:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Appraisal not found")
        return appraisal

    async def delete_appraisal(self, *, db: Session, id: UUID4) -> dict[str, Any]:
        appraisal = await self.repo.get(db=db, id=id)
        if not appraisal:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Appraisal not found")
        appraisal = await self.repo.remove(db=db, id=id)
        return appraisal

    async def get_appraisal_by_id(self, *, id: UUID4) -> AppraisalSchema:
        appraisal = await self.repo.get(id)
        if not appraisal:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Appraisal not found"
            )
        return appraisal

    async def get_appraisal_by_keywords(self, *, db: Session, tag: str) -> List[AppraisalSchema]:
        pass

    async def search_appraisals(self, *, db: Session, search: str, value: str) -> List[AppraisalSchema]:
        pass

    async def read_by_kwargs(self, *, db: Session, **kwargs) -> Any:
        return await self.repo.read_by_kwargs(self, db, kwargs)

    async def get_department_appraisals(self, db: Session, department_id):
        appraisals = await self.repo.get_all_by_ids()


appraisal_service = AppraisalService()
