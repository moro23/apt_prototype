from typing import Optional, Any, Dict, List

from pydantic import BaseModel
from pydantic import UUID4

from utils.schemas import FormField


# FormFieldTemplate
class FormFieldTemplateBase(BaseModel):
    organization_id: Optional[UUID4] = None
    model_name: Optional[str] = None
    description: Optional[str] = None
    fields: Optional[Dict[str, Any]] = None


# Properties to receive via API on creation
class FormFieldTemplateCreate(FormFieldTemplateBase):
    organization_id: UUID4
    model_name: str
    fields: List[FormField]


# Properties to receive via API on update
class FormFieldTemplateUpdate(FormFieldTemplateBase):
    pass


class FormFieldTemplateInDBBase(FormFieldTemplateBase):
    id: Optional[UUID4] = None
    creator_id: Optional[UUID4] = None
    updator_id: Optional[UUID4] = None

    class Config:
        from_attributes = True


# Additional properties to return via API
class FormFieldTemplateSchema(FormFieldTemplateInDBBase):
    pass
