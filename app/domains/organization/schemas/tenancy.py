from datetime import date
from typing import Optional

from pydantic import BaseModel
from pydantic import UUID4


# Tenancy
class TenancyBase(BaseModel):
    organization_id: Optional[UUID4] = None
    start_date: Optional[date] = None
    end_date: Optional[date] = None
    billing_cycle: Optional[str] = "Monthly"
    terms_and_conditions_id: Optional[UUID4] = None
    status: Optional[str] = "Active"


# Properties to receive via API on creation
class TenancyCreate(TenancyBase):
    organization_id: UUID4
    start_date: date
    billing_cycle: Optional[str] = "Monthly"
    terms_and_conditions_id: UUID4
    status: Optional[str] = "Active"


# Properties to receive via API on update
class TenancyUpdate(TenancyBase):
    pass


class TenancyInDBBase(TenancyBase):
    id: Optional[UUID4] = None
    creator_id: Optional[UUID4] = None
    updator_id: Optional[UUID4] = None

    class Config:
        from_attributes = True


# Additional properties to return via API
class TenancySchema(TenancyInDBBase):
    pass
