from typing import Optional, List
from pydantic import BaseModel,UUID4


# TermsAndConditions
class TermsAndConditionsBase(BaseModel):
    title: Optional[str] = None
    content: Optional[dict] = None
    version: Optional[str] = None
    is_active: Optional[bool] = True


# Properties to receive via API on creation
class TermsAndConditionsCreate(TermsAndConditionsBase):
    title: str
    content: dict
    version: str
    is_active: Optional[bool] = True


# Properties to receive via API on update
class TermsAndConditionsUpdate(TermsAndConditionsBase):
    pass


class TermsAndConditionsInDBBase(TermsAndConditionsBase):
    id: Optional[UUID4] = None
    creator_id: Optional[UUID4] = None
    updator_id: Optional[UUID4] = None

    class Config:
        from_attributes = True


# Additional properties to return via API
class TermsAndConditionsSchema(TermsAndConditionsInDBBase):
    pass



class TermsAndConditionsResponse(BaseModel):
    bk_size: int
    pg_size: int
    data: List[TermsAndConditionsSchema]