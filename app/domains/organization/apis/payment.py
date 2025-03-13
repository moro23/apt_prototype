from typing import Any, List, Literal

from fastapi import APIRouter, Depends, status
from pydantic import UUID4
from sqlalchemy.orm import Session

from db.session import get_db
from domains.auth.models import User
from domains.organization.schemas import payment as schemas
from domains.organization.services.payment import payment_service as actions
from utils.rbac import get_current_user
from utils.schemas import HTTPError

payment_router = APIRouter(prefix="/payments")


@payment_router.get(
    "/",
    response_model=List[schemas.PaymentSchema],
)
async def list_payments(
        *, db: Session = Depends(get_db),
        current_user: User = Depends(get_current_user),
        skip: int = 0,
        limit: int = 100,
        order_by: str | None = None,
        order_direction: Literal['asc', 'desc'] = 'asc'
) -> Any:
    payments = await actions.list_payments(
        db=db, skip=skip, limit=limit, order_by=order_by, order_direction=order_direction
    )
    return payments


@payment_router.post(
    "/",
    response_model=schemas.PaymentSchema,
    status_code=status.HTTP_201_CREATED,
)
async def create_payment(
        *, db: Session = Depends(get_db),
        current_user: User = Depends(get_current_user),
        payment_in: schemas.PaymentCreate
) -> Any:
    payment = await actions.create_payment(db=db, payment_in=payment_in)
    return payment


@payment_router.put(
    "/{id}",
    response_model=schemas.PaymentSchema,
    responses={status.HTTP_404_NOT_FOUND: {"model": HTTPError}},
)
async def update_payment(
        *, db: Session = Depends(get_db),
        current_user: User = Depends(get_current_user),
        id: UUID4,
        payment_in: schemas.PaymentUpdate,
) -> Any:
    payment = await actions.update_payment(db=db, id=id, payment_in=payment_in)
    return payment


@payment_router.get(
    "/{id}",
    response_model=schemas.PaymentSchema,
    responses={status.HTTP_404_NOT_FOUND: {"model": HTTPError}},
)
async def get_payment(
        *, db: Session = Depends(get_db),
        current_user: User = Depends(get_current_user),
        id: UUID4
) -> Any:
    payment = await actions.get_payment(db=db, id=id)
    return payment


@payment_router.delete(
    "/{id}",
    status_code=status.HTTP_204_NO_CONTENT,
    responses={status.HTTP_404_NOT_FOUND: {"model": HTTPError}},
)
async def delete_payment(
        *, db: Session = Depends(get_db),
        current_user: User = Depends(get_current_user),
        id: UUID4
) -> None:
    await actions.delete_payment(db=db, id=id)
