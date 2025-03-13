from datetime import datetime
from typing import Any, List, Optional

from db.session import get_db
from domains.appraisal.schemas import appraisal_submission as schemas
from domains.appraisal.services.appraisal_submission import appraisal_submission_service as actions
from domains.auth.models.users import User
from fastapi import APIRouter, Depends, Query
from fastapi import HTTPException
from pydantic import UUID4
from sqlalchemy.orm import Session
from starlette.status import HTTP_201_CREATED, HTTP_404_NOT_FOUND
from utils.rbac import get_current_user
from utils.schemas import HTTPError

appraisal_submission_router = APIRouter(prefix='/submissions')


@appraisal_submission_router.get(
    "/",
    response_model=List[schemas.AppraisalSubmissionSchema],
)
async def list_appraisal_submissions(
        db: Session = Depends(get_db),
        current_user: User = Depends(get_current_user),
        skip: int = 0, limit: int = 100,
        staff_id: UUID4 = None,
        date_from: datetime = None,
        date_to: datetime = None,
) -> Any:
    appraisal_submissions = await actions.list_appraisal_submissions(
        db=db, skip=skip, limit=limit,
        staff_id=staff_id,
        date_from=date_from,
        date_to=date_to,
    )
    return appraisal_submissions


@appraisal_submission_router.post(
    "/",
    response_model=schemas.AppraisalSubmissionSchema,
    status_code=HTTP_201_CREATED,
)
async def create_appraisal_submission(
        *, db: Session = Depends(get_db),
        current_user: User = Depends(get_current_user),
        appraisal_submission_in: schemas.AppraisalSubmissionCreate
) -> Any:
    appraisal_submission = await actions.create_appraisal_submission(
        db=db, appraisal_submission_in=appraisal_submission_in
    )
    return appraisal_submission


@appraisal_submission_router.put(
    "/{id}",
    response_model=schemas.AppraisalSubmissionSchema,
    responses={HTTP_404_NOT_FOUND: {"model": HTTPError}},
)
async def update_appraisal_submission(
        *, db: Session = Depends(get_db),
        current_user: User = Depends(get_current_user),
        id: UUID4,
        appraisal_submission_in: schemas.AppraisalSubmissionUpdate,
) -> Any:
    return await actions.update_appraisal_submission(db=db, id=id, appraisal_submission_in=appraisal_submission_in)


@appraisal_submission_router.put(
    "/{id}/update-answers/",
    response_model=schemas.AppraisalSubmissionSchema,
    responses={HTTP_404_NOT_FOUND: {"model": HTTPError}}
)
async def modify_or_add_answers(
        *, db: Session = Depends(get_db),
        current_user: User = Depends(get_current_user),
        id: UUID4,
        updates: dict,
) -> Any:
    try:
        return await actions.modify_or_add_answers(db=db, id=id, updates=updates)
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))


@appraisal_submission_router.put(
    "/{id}/update-answer/",
    response_model=schemas.AppraisalSubmissionSchema,
    responses={HTTP_404_NOT_FOUND: {"model": HTTPError}},

)
async def update_submission_answer(
        *, db: Session = Depends(get_db),
        current_user: User = Depends(get_current_user),
        id: UUID4,
        group_name: str,
        field_name: str,
        new_answer: str
):
    """
    Update a specific question's answer in a submission.
    """
    try:
        return await actions.update_submission_answer(
            db=db,
            id=id,
            group_name=group_name,
            field_name=field_name,
            new_answer=new_answer
        )
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))


@appraisal_submission_router.get(
    "/{id}",
    response_model=schemas.AppraisalSubmissionSchema,
    responses={HTTP_404_NOT_FOUND: {"model": HTTPError}},
)
async def get_appraisal_submission(
        *, db: Session = Depends(get_db),
        current_user: User = Depends(get_current_user),
        id: UUID4
) -> Any:
    appraisal_submission = await actions.get_appraisal_submission(db=db, id=id)
    if not appraisal_submission:
        raise HTTPException(status_code=HTTP_404_NOT_FOUND, detail="Appraisal submission not found")
    return appraisal_submission


@appraisal_submission_router.delete(
    "/{id}",
    response_model=dict[str, Any],
    responses={HTTP_404_NOT_FOUND: {"model": HTTPError}},
)
async def delete_appraisal_submission(
        *, db: Session = Depends(get_db),
        current_user: User = Depends(get_current_user),
        id: UUID4
) -> Any:
    appraisal_submission = await actions.get_appraisal_submission(db=db, id=id)
    if not appraisal_submission:
        raise HTTPException(status_code=HTTP_404_NOT_FOUND, detail="Appraisal submission not found")
    appraisal_submission = await actions.delete_appraisal_submission(db=db, id=id)
    return appraisal_submission


# Summaries ########################################################################################
appraisal_summary_router = APIRouter(prefix='/summaries')


@appraisal_summary_router.get(
    "/summary_results",
    response_model=dict[str, Any],
    responses={HTTP_404_NOT_FOUND: {"model": HTTPError}},
)
async def get_summary_results_endpoint(
        *, db: Session = Depends(get_db),
        current_user: User = Depends(get_current_user),
        year: Optional[int] = Query(None, description="Filter by appraisal year"),
        staff_id: Optional[UUID4] = Query(None, description="Filter by staff ID"),
        department_group_id: Optional[UUID4] = Query(None, description="Filter by department group ID"),
        cycle: Optional[str] = Query(None, description="Filter by appraisal cycle (e.g., H1, H2)")
) -> Any:
    """
    Fetch summary results grouped by group_name, filtered by year, staff_id and department_group_id.
    """
    return await actions.get_summary_results(
        db=db,
        year=year,
        staff_id=staff_id,
        department_group_id=department_group_id,
        cycle=cycle
    )


@appraisal_summary_router.get(
    "/reports",
    response_model=List[schemas.AppraisalSubmissionSchema],
    responses={HTTP_404_NOT_FOUND: {"model": HTTPError}},
)
async def get_filtered_submissions_report(
        *, db: Session = Depends(get_db),
        current_user: User = Depends(get_current_user),
        skip: int = 0, limit: int = 100,
        appraisal_year: Optional[UUID4] = Query(None, description="Filter by appraisal year"),
        cycle: Optional[str] = Query(None, description="Filter by appraisal cycle (e.g., H1, H2)"),
        department_id: Optional[UUID4] = Query(None, description="Filter by department ID"),
        staff_id: Optional[UUID4] = Query(None, description="Filter by staff ID"),
        submitted: Optional[bool] = Query(None, description="Filter by submission status"),
        completed: Optional[bool] = Query(None, description="Filter by completion status")
) -> Any:
    """
    Get filtered submission reports.
    """
    return await actions.get_filtered_submissions(
        db=db, skip=skip, limit=limit,
        appraisal_year=appraisal_year,
        cycle=cycle,
        department_id=department_id,
        staff_id=staff_id,
        submitted=submitted,
        completed=completed
    )
