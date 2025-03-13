from datetime import datetime
from typing import List, Any, Optional

from domains.appraisal.repositories.appraisal import appraisal_actions
from domains.appraisal.repositories.appraisal_input import appraisal_input_actions as appraisal_input_repo
from domains.appraisal.repositories.department_group import department_group_actions
from domains.appraisal.schemas.appraisal_input import (
    AppraisalInputSchema, AppraisalInputUpdate, AppraisalInputCreate
)
from domains.staff.repositories.department import department_actions
from fastapi import HTTPException, status
from pydantic import UUID4
from sqlalchemy.orm import Session


class AppraisalInputService:

    def __init__(self):
        self.repo = appraisal_input_repo

    async def list_appraisal_inputs(
            self, *,
            db: Session,
            skip: int = 0,
            limit: int = 100,
            appraisal_id: Optional[UUID4] = None,
            staff_id: Optional[UUID4] = None,
            appraisal_year: Optional[int] = None,
            cycle: Optional[str] = None,
            department_id: Optional[UUID4] = None,
            is_global: Optional[bool] = None,
            is_active: Optional[bool] = None,
            date_from: datetime = None,
            date_to: datetime = None,
    ) -> List[AppraisalInputSchema]:
        appraisal_inputs = await self.repo.list_appraisal_input_for_staff(
            db=db, skip=skip, limit=limit,
            is_global=is_global,
            appraisal_id=appraisal_id,
            staff_id=staff_id,
            appraisal_year=appraisal_year,
            cycle=cycle,
            department_id=department_id,
            is_active=is_active,
            date_from=date_from,
            date_to=date_to,
        )
        if not appraisal_inputs: return []
        appraisal_ids = {
            input.appraisal_id for input in appraisal_inputs if input.appraisal_id is not None
        }
        department_group_ids = {
            input.department_group_id for input in appraisal_inputs if
            input.department_group_id is not None
        }

        department_ids = {
            id for input in appraisal_inputs
            if input.department_ids is not None
            for id in input.department_ids
            if id is not None
        }

        appraisals_map = {
            str(a.id): a for a in await appraisal_actions.get_all_by_ids_silently(db=db, ids=list(appraisal_ids))
        } if appraisal_ids else dict()

        department_groups_map = {
            str(d.id): d for d in
            await department_group_actions.get_all_by_ids_silently(db=db, ids=list(department_group_ids))
        } if department_group_ids else dict()

        departments_map = {
            str(d.id): d for d in await department_actions.get_all_by_ids_silently(db=db, ids=list(department_ids))
        } if department_ids else dict()

        return [
            AppraisalInputSchema(
                **{k: v for k, v in input.__dict__.items() if k != '_sa_instance_state'},
                departments=[
                    departments_map.get(id)
                    for id in (input.department_ids or [])
                    if id is not None and id in departments_map
                ],
                appraisal=appraisals_map.get(str(input.appraisal_id)) if input.appraisal_id is not None else None,
                department_group=department_groups_map.get(
                    str(input.department_group_id)) if input.department_group_id is not None else None
            )
            for input in appraisal_inputs
        ]

    async def create_appraisal_input(self, *, db: Session,
                                     appraisal_input_in: AppraisalInputCreate) -> AppraisalInputSchema:
        appraisal_input = await self.repo.create(db=db, data=appraisal_input_in)
        return appraisal_input

    async def update_appraisal_input(
            self, *, db: Session, id: UUID4, appraisal_input_in: AppraisalInputUpdate
    ) -> AppraisalInputSchema:
        appraisal_input = await self.repo.get(db=db, id=id)
        if not appraisal_input:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Appraisal input not found")
        appraisal_input = await self.repo.update(db=db, db_obj=appraisal_input, data=appraisal_input_in)
        return appraisal_input

    async def get_appraisal_input(self, *, db: Session, id: UUID4) -> AppraisalInputSchema:
        appraisal_input = await self.repo.get(db=db, id=id)
        if not appraisal_input:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Appraisal input not found")

        appraisal_input_dict = appraisal_input.__dict__
        appraisal_input_dict.pop('_sa_instance_state', None)

        return AppraisalInputSchema(
            **appraisal_input_dict,
            departments=await department_actions.get_all_by_ids_silently(db=db, ids=appraisal_input.department_ids),
            appraisal=await appraisal_actions.get(db=db, id=appraisal_input.appraisal_id),
            department_group=await department_group_actions.get(db=db, id=appraisal_input.department_group_id),
        )

    async def delete_appraisal_input(self, *, db: Session, id: UUID4) -> dict[str, Any]:
        appraisal_input = await self.repo.get(db=db, id=id)
        if not appraisal_input:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Appraisal input not found")
        appraisal_input = await self.repo.remove(db=db, id=id)
        return appraisal_input

    async def get_appraisal_input_by_id(self, *, id: UUID4) -> AppraisalInputSchema:
        appraisal_input = await self.repo.get(id)
        if not appraisal_input:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Appraisal input not found"
            )
        return appraisal_input

    async def get_appraisal_input_by_keywords(self, *, db: Session, tag: str) -> List[AppraisalInputSchema]:
        pass

    async def search_appraisal_inputs(self, *, db: Session, search: str, value: str) -> List[AppraisalInputSchema]:
        pass

    async def read_by_kwargs(self, *, db: Session, **kwargs) -> Any:
        return await self.repo.get_by_kwargs(self, db, kwargs)


appraisal_input_service = AppraisalInputService()
