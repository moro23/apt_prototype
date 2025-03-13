from typing import Optional

from pydantic import BaseModel
from pydantic import UUID4


# AppraisalTemplate
class AppraisalTemplateBase(BaseModel):
    name: Optional[str] = None
    description: Optional[str] = None
    org_type: Optional[str] = None


# Properties to receive via API on creation
class AppraisalTemplateCreate(AppraisalTemplateBase):
    name: str


# Properties to receive via API on update
class AppraisalTemplateUpdate(AppraisalTemplateBase):
    pass


class AppraisalTemplateInDBBase(AppraisalTemplateBase):
    id: Optional[UUID4] = None
    creator_id: Optional[UUID4] = None
    updator_id: Optional[UUID4] = None

    class Config:
        from_attributes = True


# Additional properties to return via API
class AppraisalTemplateSchema(AppraisalTemplateInDBBase):
    pass
