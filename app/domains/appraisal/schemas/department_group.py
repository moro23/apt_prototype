from typing import Optional

from pydantic import BaseModel
from pydantic import UUID4


# DepartmentGroup
class DepartmentGroupBase(BaseModel):
    department_id: Optional[UUID4] = None
    name: Optional[str] = None


# Properties to receive via API on creation
class DepartmentGroupCreate(DepartmentGroupBase):
    name: str


# Properties to receive via API on update
class DepartmentGroupUpdate(DepartmentGroupBase):
    pass


class DepartmentGroupInDBBase(DepartmentGroupBase):
    id: Optional[UUID4] = None
    creator_id: Optional[UUID4] = None
    updator_id: Optional[UUID4] = None

    class Config:
        from_attributes = True


# Additional properties to return via API
class DepartmentGroupSchema(DepartmentGroupInDBBase):
    pass
