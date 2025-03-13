from datetime import datetime
from typing import List, Optional
from uuid import UUID

from crud.base import CRUDBase
from domains.appraisal.models import Appraisal
from domains.appraisal.models.appraisal_input import AppraisalInput
from domains.appraisal.schemas.appraisal_input import (
    AppraisalInputCreate, AppraisalInputUpdate
)
from domains.staff.repositories.staff import staff_actions
from sqlalchemy import or_, desc
from sqlalchemy.orm import Session


class CRUDAppraisalInput(CRUDBase[AppraisalInput, AppraisalInputCreate, AppraisalInputUpdate]):
    async def list_appraisal_input_for_staff(
            self, *, db: Session,
            skip: int = 0, limit: int = 100,
            appraisal_id: Optional[UUID] = None,
            staff_id: Optional[UUID] = None,
            appraisal_year: Optional[int] = None,
            cycle: Optional[str] = None,
            department_id: Optional[UUID] = None,
            is_global: Optional[bool] = None,
            is_active: Optional[bool] = None,
            date_from: datetime = None,
            date_to: datetime = None,
    ) -> List[AppraisalInput]:
        """
        Fetch form inputs (appraisal_inputs) filtered by staff ID, year, cycle, department, and designation.
        Designation takes precedence over department.
        """
        # Start with the base query for form_inputs
        query = (
            db.query(AppraisalInput)
            .join(Appraisal)
        )

        # Filter by appraisal year and cycle
        if appraisal_year:
            query = query.filter(Appraisal.year == appraisal_year)
        if cycle:
            query = query.filter(Appraisal.cycle == cycle)

        # Staff-specific filters
        if staff_id:
            staff = await staff_actions.get(db=db, id=staff_id)
            if not staff:
                raise ValueError(f"Staff with ID {staff_id} not found")

            # Create filters for both designation and department
            query = query.filter(or_(
                AppraisalInput.department_ids.contains([staff.department_id])
            ))

        elif department_id:
            query = query.filter(AppraisalInput.department_ids.contains([department_id]))

        if is_global is not None:
            query = query.filter(AppraisalInput.is_global == is_global)
        if is_active is not None:
            query = query.filter(AppraisalInput.is_active == is_active)

        if appraisal_id:
            query = query.filter(AppraisalInput.appraisal_id == appraisal_id)

        if date_to: query = query.filter(AppraisalInput.created_date <= date_to)
        if date_from: query = query.filter(AppraisalInput.created_date >= date_from)

        return query.order_by(desc(AppraisalInput.created_date)).offset(skip).limit(limit).all()


appraisal_input_actions = CRUDAppraisalInput(AppraisalInput)
