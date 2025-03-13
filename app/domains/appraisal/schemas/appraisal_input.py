from typing import Optional, List

from pydantic import BaseModel
from pydantic import UUID4

from domains.appraisal.schemas.appraisal import AppraisalSchema
from domains.appraisal.schemas.department_group import DepartmentGroupSchema
from domains.staff.schemas.department import DepartmentSchema
from utils.schemas import FormField


class AppraisalFormInputFields(BaseModel):
    group_name: str
    fields: Optional[List[FormField]]


# AppraisalInput
class AppraisalInputBase(BaseModel):
    appraisal_id: Optional[UUID4] = None
    department_group_id: Optional[UUID4] = None
    form_fields: List[AppraisalFormInputFields]
    department_ids: Optional[List[UUID4]] = None
    is_global: Optional[bool] = None
    is_active: Optional[bool] = None


# Properties to receive via API on creation
class AppraisalInputCreate(AppraisalInputBase):
    appraisal_id: UUID4


# Properties to receive via API on update
class AppraisalInputUpdate(AppraisalInputBase):
    pass


class AppraisalInputInDBBase(AppraisalInputBase):
    id: Optional[UUID4] = None
    creator_id: Optional[UUID4] = None
    updator_id: Optional[UUID4] = None

    class Config:
        from_attributes = True


# Additional properties to return via API
class AppraisalInputSchema(AppraisalInputInDBBase):
    appraisal: Optional[AppraisalSchema] = None
    department_group: Optional[DepartmentGroupSchema] = None
    departments: Optional[List[DepartmentSchema]] = None
