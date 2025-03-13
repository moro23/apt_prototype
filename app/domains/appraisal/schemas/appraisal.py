from datetime import date
from typing import Optional, List

from pydantic import BaseModel
from pydantic import UUID4

from utils.schemas import FormField


# Appraisal
class AppraisalBase(BaseModel):
    name: Optional[str] = None
    year: Optional[int] = None
    description: Optional[str] = None
    cycle: Optional[str] = None
    form_fields: Optional[FormField] = None
    period_from: Optional[date] = None
    period_to: Optional[date] = None


# Properties to receive via API on creation
class AppraisalCreate(AppraisalBase):
    name: str


# Properties to receive via API on update
class AppraisalUpdate(AppraisalBase):
    pass


class AppraisalInDBBase(AppraisalBase):
    id: Optional[UUID4] = None
    creator_id: Optional[UUID4] = None
    updator_id: Optional[UUID4] = None

    class Config:
        from_attributes = True


# Additional properties to return via API
class AppraisalSchema(AppraisalInDBBase):
    pass


class RelatedAppraisalFields(BaseModel):
    field_type: Optional[str] = None
    field_name: Optional[str] = None
    field_text: Optional[str] = None
    field_hint: Optional[str] = None
    order: Optional[int] = None
    required: Optional[bool] = None
    metadata: Optional[dict] = None


class RelatedAppraisalFormInputFields(BaseModel):
    group_name: Optional[str] = None
    fields: Optional[List[RelatedAppraisalFields]] = None


class RelatedAppraisalInput(BaseModel):
    department_group_id: Optional[UUID4] = None
    form_template: Optional[List[RelatedAppraisalFormInputFields]] = None
    department_ids: Optional[List[UUID4]] = None
    is_global: Optional[bool] = None
    is_active: Optional[bool] = None


class SingleAppraisalSchema(AppraisalInDBBase):
    inputs: Optional[List[RelatedAppraisalInput]] = None
