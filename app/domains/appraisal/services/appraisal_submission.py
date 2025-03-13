from datetime import datetime
from typing import List, Any, Optional

from config.logger import log
from domains.appraisal.repositories.appraisal_submission import (
    appraisal_submission_actions as appraisal_submission_repo
)
from domains.appraisal.schemas.appraisal_submission import (
    AppraisalSubmissionSchema, AppraisalSubmissionUpdate, AppraisalSubmissionCreate
)
from fastapi import HTTPException, status
from pydantic import ValidationError, UUID4
from sqlalchemy.orm import Session


class AppraisalSubmissionService:

    def __init__(self):
        self.repo = appraisal_submission_repo

    async def get_filtered_submissions(
            self, *, db: Session,
            skip: int = 0, limit: int = 100,
            appraisal_year: Optional[int] = None,
            cycle: Optional[str] = None,
            department_id: Optional[UUID4] = None,
            staff_id: Optional[UUID4] = None,
            submitted: Optional[bool] = None,
            completed: Optional[bool] = None
    ) -> List[AppraisalSubmissionSchema]:
        appraisal_submissions = await self.repo.get_filtered_submissions(
            db=db, skip=skip, limit=limit,
            appraisal_year=appraisal_year,
            cycle=cycle,
            department_id=department_id,
            staff_id=staff_id,
            submitted=submitted,
            completed=completed,
        )
        return appraisal_submissions

    async def list_appraisal_submissions(
            self, *, db: Session, skip: int = 0, limit: int = 100,
            staff_id: str = None,
            date_from: datetime = None,
            date_to: datetime = None,
    ) -> List[AppraisalSubmissionSchema]:
        appraisal_submissions = await self.repo.get_all(
            db=db, skip=skip, limit=limit, staff_id=staff_id,
            date_from=date_from, date_to=date_to,
        )
        return appraisal_submissions

    async def create_appraisal_submission(
            self, *, db: Session, appraisal_submission_in: AppraisalSubmissionCreate
    ) -> AppraisalSubmissionSchema:
        appraisal_submission = await self.repo.create(db=db, data=appraisal_submission_in)
        return appraisal_submission

    async def update_appraisal_submission(
            self, *, db: Session, id: UUID4, appraisal_submission_in: AppraisalSubmissionUpdate
    ) -> AppraisalSubmissionSchema:
        appraisal_submission = await self.repo.get(db=db, id=id)
        if not appraisal_submission:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Appraisal submission not found"
            )
        if appraisal_submission.completed:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Appraisal submission already completed"
            )
        appraisal_submission = await self.repo.update(db=db, db_obj=appraisal_submission,
                                                      data=appraisal_submission_in)
        return appraisal_submission

    async def get_appraisal_submission(self, *, db: Session, id: UUID4) -> AppraisalSubmissionSchema:
        appraisal_submission = await self.repo.get(db=db, id=id)
        if not appraisal_submission:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Appraisal submission not found")
        return appraisal_submission

    async def delete_appraisal_submission(self, *, db: Session, id: UUID4) -> dict[str, Any]:
        appraisal_submission = await self.repo.get(db=db, id=id)
        if not appraisal_submission:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Appraisal submission not found")
        appraisal_submission = await self.repo.remove(db=db, id=id)
        return appraisal_submission

    async def get_appraisal_submission_by_id(self, *, id: UUID4) -> AppraisalSubmissionSchema:
        appraisal_submission = await self.repo.get(id)
        if not appraisal_submission:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Appraisal submission not found"
            )
        return appraisal_submission

    async def get_appraisal_submission_by_keywords(self, *, db: Session, tag: str) -> List[AppraisalSubmissionSchema]:
        pass

    async def search_appraisal_submissions(self, *, db: Session, search: str, value: str) -> List[
        AppraisalSubmissionSchema]:
        pass

    async def read_by_kwargs(self, *, db: Session, **kwargs) -> Any:
        return await self.repo.read_by_kwargs(self, db, **kwargs)

    async def list_appraisal_submissions_by_staff(
            self, *, db: Session, skip: int = 0, limit: int = 100, staff_id: UUID4, year: int
    ):
        return await self.repo.get_all_appraisal_submissions_by_staff(
            db=db, skip=skip, limit=limit, staff_id=staff_id, year=year
        )

    async def list_appraisal_submissions_by_department(
            self, *, db: Session, skip: int = 0, limit: int = 100, department_id: UUID4, year: int,
    ):
        return await self.repo.get_all_appraisal_submissions_by_department(
            db=db, skip=skip, limit=limit, department_id=department_id, year=year
        )

    async def update_submission_answer(
            self, *, db,
            id: UUID4,
            group_name: str,
            field_name: str,
            new_answer: str,
    ):
        return await self.repo.update_answer_in_submission(
            db=db, id=id, group_name=group_name, field_name=field_name, new_answer=new_answer
        )

    async def modify_or_add_answers(
            self, *, db: Session, id: int, updates: dict
    ) -> AppraisalSubmissionSchema:
        try:
            return await self.repo.modify_or_add_answers(
                db=db, id=id, updates=updates
            )
        except ValidationError as e:
            raise HTTPException(
                status_code=status.HTTP_422_UNPROCESSABLE_ENTITY, detail=str(e)
            )
        except AttributeError:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST, detail='Incorrect data format received.'
            )
        except:
            log.exception('Failed to modify or add appraisal submission answers')
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail='An error occurred.'
            )

    async def get_summary_results(
            self, *, db: Session,
            year: int = None,
            staff_id: UUID4 = None,
            department_group_id: UUID4 = None,
            cycle: str = None
    ) -> dict[str, Any]:
        return await self.repo.get_summary_results(
            db=db, year=year, staff_id=staff_id, department_group_id=department_group_id, cycle=cycle
        )


appraisal_submission_service = AppraisalSubmissionService()
