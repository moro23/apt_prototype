from typing import Optional, List

from pydantic import BaseModel
from pydantic import UUID4

from utils.schemas import FormField


# Department
class DepartmentBase(BaseModel):
    name: Optional[str] = None
    form_fields: Optional[List[FormField]] = None


# Properties to receive via API on creation
class DepartmentCreate(DepartmentBase):
    name: str


# Properties to receive via API on update
class DepartmentUpdate(DepartmentBase):
    pass


class DepartmentInDBBase(DepartmentBase):
    id: Optional[UUID4] = None
    creator_id: Optional[UUID4] = None
    updator_id: Optional[UUID4] = None

    class Config:
        from_attributes = True


# Additional properties to return via API
class DepartmentSchema(DepartmentInDBBase):
    pass
