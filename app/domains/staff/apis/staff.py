from typing import Any, List, Literal

from fastapi import APIRouter, Depends, status
from pydantic import UUID4
from sqlalchemy.orm import Session

from db.session import get_db
from domains.auth.models import User
from domains.staff.schemas import staff as schemas
from domains.staff.services.staff import staff_service as actions
from utils.rbac import get_current_user
from utils.schemas import HTTPError

staff_router = APIRouter()


@staff_router.get(
    "/",
    response_model=List[schemas.StaffSchema],
)
async def list_staffs(
        *, db: Session = Depends(get_db),
        current_user: User = Depends(get_current_user),
        skip: int = 0,
        limit: int = 100,
        order_by: str | None = None,
        order_direction: Literal['asc', 'desc'] = 'asc'
) -> Any:
    staffs = await actions.list_staffs(
        db=db, skip=skip, limit=limit, order_by=order_by, order_direction=order_direction
    )
    return staffs


@staff_router.post(
    "/",
    response_model=schemas.StaffSchema,
    status_code=status.HTTP_201_CREATED,
)
async def create_staff(
        *, db: Session = Depends(get_db),
        current_user: User = Depends(get_current_user),
        staff_in: schemas.StaffCreate
) -> Any:
    staff = await actions.create_staff(db=db, staff_in=staff_in)
    return staff


@staff_router.put(
    "/{id}",
    response_model=schemas.StaffSchema,
    responses={status.HTTP_404_NOT_FOUND: {"model": HTTPError}},
)
async def update_staff(
        *, db: Session = Depends(get_db),
        current_user: User = Depends(get_current_user),
        id: UUID4,
        staff_in: schemas.StaffUpdate,
) -> Any:
    staff = await actions.update_staff(db=db, id=id, staff_in=staff_in)
    return staff


@staff_router.get(
    "/{id}",
    response_model=schemas.StaffSchema,
    responses={status.HTTP_404_NOT_FOUND: {"model": HTTPError}},
)
async def get_staff(
        *, db: Session = Depends(get_db),
        current_user: User = Depends(get_current_user),
        id: UUID4
) -> Any:
    staff = await actions.get_staff(db=db, id=id)
    return staff


@staff_router.delete(
    "/{id}",
    status_code=status.HTTP_204_NO_CONTENT,
)
async def delete_staff(
        *, db: Session = Depends(get_db),
        current_user: User = Depends(get_current_user),
        id: UUID4
) -> None:
    await actions.delete_staff(db=db, id=id)
