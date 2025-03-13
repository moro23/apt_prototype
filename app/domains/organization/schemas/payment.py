from datetime import datetime
from typing import Optional

from pydantic import BaseModel
from pydantic import UUID4


# Payment
class PaymentBase(BaseModel):
    bill_id: Optional[UUID4] = None
    amount_paid: Optional[float] = None
    payment_date: Optional[datetime] = None
    payment_method: Optional[str] = None
    transaction_id: Optional[str] = None
    status: Optional[str] = "Success"


# Properties to receive via API on creation
class PaymentCreate(PaymentBase):
    bill_id: UUID4
    amount_paid: float
    payment_date: Optional[datetime] = None
    payment_method: str
    transaction_id: str
    status: Optional[str] = "Success"


# Properties to receive via API on update
class PaymentUpdate(PaymentBase):
    pass


class PaymentInDBBase(PaymentBase):
    id: Optional[UUID4] = None
    creator_id: Optional[UUID4] = None
    updator_id: Optional[UUID4] = None

    class Config:
        from_attributes = True


# Additional properties to return via API
class PaymentSchema(PaymentInDBBase):
    pass
