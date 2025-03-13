from datetime import date
from typing import Optional,List
from pydantic import BaseModel,UUID4


# Bill
class BillBase(BaseModel):
    tenancy_id: Optional[UUID4] = None
    amount: Optional[float] = None
    due_date: Optional[date] = None
    status: Optional[str] = "Unpaid"


# Properties to receive via API on creation
class BillCreate(BillBase):
    tenancy_id: UUID4
    amount: float
    due_date: date
    status: Optional[str] = "Unpaid"


# Properties to receive via API on update
class BillUpdate(BillBase):
    pass


class BillInDBBase(BillBase):
    id: Optional[UUID4] = None
    creator_id: Optional[UUID4] = None
    updator_id: Optional[UUID4] = None

    class Config:
        from_attributes = True


# Additional properties to return via API
class BillSchema(BillInDBBase):
    pass




class BillsResponse(BaseModel):
    bk_size: int
    pg_size: int
    data: List[BillSchema]