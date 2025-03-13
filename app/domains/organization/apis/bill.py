from typing import Any, List

from fastapi import APIRouter, Depends, status
from pydantic import UUID4
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import Session

from db.session import get_db
from domains.auth.models import User
from domains.organization.repositories.bill import bills
from domains.organization.schemas import bill as schemas
from domains.organization.services.bill import bill_service as actions
from utils.cls import ContentQueryChecker
from utils.rbac import get_current_user
from utils.schemas import HTTPError

bill_router = APIRouter(prefix="/bills")


@bill_router.get(
    "/",
    response_model=List[schemas.BillsResponse],
)
# @ContentQueryChecker(bills.model.c(), None)
async def list_bills(
        db: AsyncSession = Depends(get_db),
        current_user: User = Depends(get_current_user),
        **params
) -> Any:
    bills = await actions.list_bills(db, **params)
    return bills


@bill_router.post(
    "/",
    response_model=schemas.BillSchema,
    status_code=status.HTTP_201_CREATED,
)
async def create_bill(
        *, db: Session = Depends(get_db),
        current_user: User = Depends(get_current_user),
        bill_in: schemas.BillCreate
) -> Any:
    bill = await actions.create_bill(db=db, bill_in=bill_in)
    return bill


@bill_router.put(
    "/{id}",
    response_model=schemas.BillSchema,
    responses={status.HTTP_404_NOT_FOUND: {"model": HTTPError}},
)
async def update_bill(
        *, db: Session = Depends(get_db),
        current_user: User = Depends(get_current_user),
        id: UUID4,
        bill_in: schemas.BillUpdate,
) -> Any:
    bill = await actions.update_bill(db=db, id=id, bill_in=bill_in)
    return bill


@bill_router.get(
    "/{id}",
    response_model=schemas.BillSchema,
    responses={status.HTTP_404_NOT_FOUND: {"model": HTTPError}},
)
async def get_bill(
        *, db: Session = Depends(get_db),
        current_user: User = Depends(get_current_user),
        id: UUID4
) -> Any:
    bill = await actions.get_bill(db=db, id=id)
    return bill


@bill_router.delete(
    "/{id}",
    status_code=status.HTTP_204_NO_CONTENT,
    responses={status.HTTP_404_NOT_FOUND: {"model": HTTPError}},
)
async def delete_bill(
        *, db: Session = Depends(get_db),
        current_user: User = Depends(get_current_user),
        id: UUID4
) -> None:
    await actions.delete_bill(db=db, id=id)
