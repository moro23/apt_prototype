from typing import Optional, Any, Dict, List

from pydantic import BaseModel
from pydantic import UUID4


# OrganizationBranch
class OrganizationBranchBase(BaseModel):
    organization_id: Optional[str] = None
    name: Optional[str] = None
    location: Optional[Dict[str, Any]] = None


# Properties to receive via API on creation
class OrganizationBranchCreate(OrganizationBranchBase):
    organization_id: str
    name: str


# Properties to receive via API on update
class OrganizationBranchUpdate(OrganizationBranchBase):
    pass


class OrganizationBranchInDBBase(OrganizationBranchBase):
    id: Optional[UUID4] = None
    creator_id: Optional[UUID4] = None
    updator_id: Optional[UUID4] = None

    class Config:
        from_attributes = True


# Additional properties to return via API
class OrganizationBranchSchema(OrganizationBranchInDBBase):
    pass




class OrganizationBranchResponse(BaseModel):
    bk_size: int
    pg_size: int
    data: List[OrganizationBranchSchema]