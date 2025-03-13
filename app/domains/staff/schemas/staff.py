from typing import Optional

from pydantic import BaseModel
from pydantic import UUID4

from utils.schemas import FormField


class StaffBase(BaseModel):
    organization_id: Optional[UUID4] = None
    department_id: Optional[UUID4] = None
    user_id: Optional[UUID4] = None
    form_fields: Optional[FormField] = None


# Properties to receive via API on creation
class StaffCreate(StaffBase):
    organization_id: UUID4
    user_id: UUID4
    form_fields: FormField


# Properties to receive via API on update
class StaffUpdate(StaffBase):
    pass


class StaffInDBBase(StaffBase):
    id: Optional[UUID4] = None
    creator_id: Optional[UUID4] = None
    updator_id: Optional[UUID4] = None

    class Config:
        from_attributes = True


# Additional properties to return via API
class StaffSchema(StaffInDBBase):
    pass
