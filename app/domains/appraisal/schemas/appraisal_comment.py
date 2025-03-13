from typing import Optional

from pydantic import BaseModel
from pydantic import UUID4


# AppraisalComment
class AppraisalCommentBase(BaseModel):
    organization_id: Optional[UUID4] = None
    content: Optional[str] = None
    commenter_id: Optional[UUID4] = None


# Properties to receive via API on creation
class AppraisalCommentCreate(AppraisalCommentBase):
    organization_id: UUID4
    content: str
    commenter_id: UUID4


# Properties to receive via API on update
class AppraisalCommentUpdate(AppraisalCommentBase):
    pass


class AppraisalCommentInDBBase(AppraisalCommentBase):
    id: Optional[UUID4] = None
    creator_id: Optional[UUID4] = None
    updator_id: Optional[UUID4] = None

    class Config:
        from_attributes = True


# Additional properties to return via API
class AppraisalCommentSchema(AppraisalCommentInDBBase):
    pass
