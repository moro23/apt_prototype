from datetime import datetime
from typing import Any, List, Optional, Sequence

from pydantic import UUID4
from sqlalchemy import desc
from sqlalchemy.orm import Session
from sqlalchemy.orm.attributes import flag_modified

from crud.base import CRUDBase
from domains.appraisal.models import Appraisal, DepartmentGroup, AppraisalInput
from domains.appraisal.models.appraisal_submission import AppraisalSubmission
from domains.appraisal.schemas.appraisal_submission import (
    AppraisalSubmissionCreate, AppraisalSubmissionUpdate
)
from domains.staff.models import Staff, Department


class CRUDAppraisalSubmission(CRUDBase[AppraisalSubmission, AppraisalSubmissionCreate, AppraisalSubmissionUpdate]):
    async def get_filtered_submissions(
            self, *, db: Session,
            skip: int = 0, limit: int = 100,
            appraisal_year: Optional[int] = None,
            cycle: Optional[str] = None,
            department_id: Optional[UUID4] = None,
            staff_id: Optional[UUID4] = None,
            submitted: Optional[bool] = None,
            completed: Optional[bool] = None
    ) -> Sequence[AppraisalSubmission]:
        """
        Fetch submissions filtered by various parameters.
        """
        query = (
            db.query(AppraisalSubmission)
            .join(AppraisalInput)
            .join(Appraisal)
            .join(Staff)
            .join(DepartmentGroup)
            .join(Department)
        )

        # Apply dynamic filters
        if appraisal_year: query = query.filter(Appraisal.year == appraisal_year)
        if cycle: query = query.filter(Appraisal.cycle == cycle)
        if department_id: query = query.filter(Department.id == department_id)
        if staff_id: query = query.filter(AppraisalSubmission.staff_id == staff_id)
        if submitted is not None: query = query.filter(AppraisalSubmission.submitted == submitted)
        if completed is not None: query = query.filter(AppraisalSubmission.completed == completed)

        return query.offset(skip).limit(limit).all()

    async def summarize_submissions_by_form_input(self, *, db: Session) -> List[dict]:
        """
        Summarize submissions grouped by form_input.
        """
        query = (
            db.query(AppraisalInput, AppraisalSubmission)
            .join(AppraisalSubmission)
        )

        summaries = {}
        for form_input, submission in query:
            form_input_id = form_input.id
            if form_input_id not in summaries:
                summaries[form_input_id] = {
                    "form_input_name": form_input.name,
                    "year": form_input.year,
                    "cycle": form_input.cycle,
                    "submissions": []
                }

            summaries[form_input_id]["submissions"].append({
                "staff_id": submission.staff_id,
                "submitted": submission.submitted,
                "completed": submission.completed,
                "data": submission.data,
                "updated_at": submission.updated_at
            })

        return list(summaries.values())

    async def get_all(
            self, db: Session, *, skip: int = 0, limit: int = 100,
            staff_id: str = None,
            date_from: datetime = None,
            date_to: datetime = None,
    ) -> List[AppraisalSubmission]:
        query = db.query(self.model)

        if staff_id is not None: query = query.filter(self.model.staff_id == staff_id)
        if date_to: query = query.filter(self.model.started_at <= date_to)
        if date_from: query = query.filter(self.model.started_at >= date_from)

        query = query.order_by(desc(self.model.created_date))
        return query.offset(skip).limit(limit).all()

    async def get_all_appraisal_submissions_by_staff(
            self, *, db: Session, skip: int = 0, limit: int = 100, staff_id: UUID4, year: int
    ) -> Optional[List[AppraisalSubmission]]:
        submissions = (
            db.query(self.model)
            .join(AppraisalInput)
            .join(Appraisal)
            .filter(self.model.staff_id == staff_id, Appraisal.year == year)
            .offset(skip).limit(limit)
            .all()
        )
        return submissions

    async def get_all_appraisal_submissions_by_department(
            self, *, db: Session, skip: int = 0, limit: int = 100, department_id: UUID4, year: int,
    ) -> Optional[List[AppraisalSubmission]]:
        submissions = (
            db.query(AppraisalSubmission)
            .join(AppraisalSubmission.appraisal_input)
            .join(AppraisalInput.department_group)
            .join(DepartmentGroup.department)
            .join(AppraisalInput.appraisal)
            .filter(Department.id == department_id)
            .filter(Appraisal.year == year)
            .offset(skip).limit(limit).all()
        )
        return submissions

    async def update_answer_in_submission(
            self, *, db: Session, id: UUID4, group_name: str, field_name: str, new_answer: str
    ) -> AppraisalSubmission:
        """
        Update a specific question's answer in a submission.
        """
        submission = db.query(self.model).filter(self.model.id == id).first()

        if not submission:
            raise ValueError(f"Submission not found.")

        if submission.completed:
            raise ValueError(f"Submission is marked as complete and cannot be updated.")

        # Check if the group exists in the JSON data
        if group_name not in submission.data:
            raise ValueError(f"Group '{group_name}' not found in the submission data.")

        # Check if the question exists in the group
        if field_name not in submission.data[group_name]:
            raise ValueError(f"Question '{field_name}' not found in the group '{group_name}'.")

        # Update the specific question's answer
        submission.data[group_name][field_name] = new_answer

        flag_modified(submission, "data")
        db.commit()
        db.refresh(submission)
        return submission

    async def modify_or_add_answers(
            self, *, db: Session, id: int, updates: dict
    ) -> AppraisalSubmission:
        """
        Modify existing answers and add new ones in the submission data field.

        Args:
            db: Database session.
            id: ID of the submission to update.
            updates: A dictionary where keys are group names, and values are dictionaries of
                     question IDs and their new answers.

        Returns:
            Submission: The updated submission.
        """
        submission = db.query(self.model).filter(self.model.id == id).first()

        if not submission:
            raise ValueError(f"Submission not found.")

        if submission.completed:
            raise ValueError(f"Submission is marked as complete and cannot be updated.")

        # Update or add answers
        for group_name, questions in updates.items():
            if group_name not in submission.data:
                # Add new group if it doesn't exist
                submission.data[group_name] = {}

            for field_name, new_answer in questions.items():
                # Update existing question or add new one
                submission.data[group_name][field_name] = new_answer

        flag_modified(submission, "data")
        db.commit()
        db.refresh(submission)
        return submission

    async def get_summary_results(
            self, *, db: Session,
            year: int = None,
            staff_id: UUID4 = None,
            department_group_id: UUID4 = None,
            cycle: str = None
    ) -> dict[str, Any]:
        """
        Fetch summary results grouped by group_name, filtered by year, staff_id, and department_group_id
        """
        query = (
            db.query(AppraisalSubmission)
            .join(Appraisal, AppraisalSubmission.appraisal_id == Appraisal.id)
            .join(Staff, AppraisalSubmission.staff_id == Staff.id)
            .join(AppraisalInput, AppraisalSubmission.appraisal_input_id == AppraisalInput.id)
            .join(DepartmentGroup, AppraisalInput.department_group_id == DepartmentGroup.id)
        )

        # Apply filters dynamically
        if year:
            query = query.filter(Appraisal.year == year)
        if staff_id:
            query = query.filter(AppraisalSubmission.staff_id == staff_id)
        if department_group_id:
            query = query.filter(AppraisalInput.department_group_id == department_group_id)
        if cycle:
            query = query.filter(Appraisal.cycle == cycle)

        submissions = query.all()

        # Results organized by staff
        summary_results = {}

        for submission in submissions:
            appraisal = submission.appraisal
            appraisal_id = str(appraisal.id)
            staff_id = str(submission.staff_id)
            form_template = submission.appraisal_input.form_fields

            if staff_id not in summary_results:
                summary_results[staff_id] = {
                    "appraisal_id": appraisal_id,
                    "staff_id": staff_id,
                    "groups": {}
                }

            for group in form_template:
                group_name = group["group_name"]

                if group_name not in summary_results[staff_id]["groups"]:
                    summary_results[staff_id]["groups"][group_name] = []

                for field in group["fields"]:
                    field_name = field["field_name"]
                    field_text = field["field_text"]
                    answer = submission.data.get(group_name, {}).get(field_name, None)

                    summary_results[staff_id]["groups"][group_name].append({
                        "field_name": field_name,
                        "field_text": field_text,
                        "answer": answer
                    })
        return summary_results


appraisal_submission_actions = CRUDAppraisalSubmission(AppraisalSubmission)
