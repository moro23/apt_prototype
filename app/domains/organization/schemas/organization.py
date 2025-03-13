from typing import Optional, List

from pydantic import BaseModel, EmailStr, UUID4

from domains.auth.schemas.roles import RoleSchema


# Organization
class OrganizationBase(BaseModel):
    name: Optional[str] = None
    org_email: Optional[str] = None
    country: Optional[str] = None
    org_type: Optional[str] = None
    is_single_branch: Optional[bool] = None
    employee_range: Optional[str] = None
    domain_name: Optional[str] = None
    is_active: Optional[bool] = True
    subscription_plan: Optional[str] = "Basic"


# Properties to receive via API on creation
class OrganizationCreate(OrganizationBase):
    name: str
    org_email: str
    country: str
    org_type: str
    employee_range: str
    domain_name: str


# Properties to receive via API on update
class OrganizationUpdate(OrganizationBase):
    pass


class OrganizationInDBBase(OrganizationBase):
    id: Optional[UUID4] = None
    creator_id: Optional[UUID4] = None
    updator_id: Optional[UUID4] = None

    class Config:
        from_attributes = True


# Additional properties to return via API
class OrganizationSchema(OrganizationInDBBase):
    pass


class OrganizationResponse(BaseModel):
    bk_size: int
    pg_size: int
    data: List[OrganizationSchema]


class UserResponse(BaseModel):
    id: UUID4
    username: str
    email: EmailStr
    role: Optional[RoleSchema]


class OrganizationWithUsersResponse(BaseModel):
    id: UUID4
    name: str
    org_email: EmailStr
    country: str
    org_type: str
    is_single_branch: bool
    employee_range: Optional[str] = None
    domain_name: str
    is_active: bool
    subscription_plan: Optional[str] = None
    users: List[UserResponse] = []
    roles: List[RoleSchema] = []

    class Config:
        from_attributes = True
