from typing import Optional, Any, Dict

from pydantic import BaseModel
from pydantic import UUID4


class OrganizationLogo(BaseModel):
    url: str
    alt_text: Optional[str] = None
    is_main: bool = False


# OrganizationSettings
class OrganizationSettingsBase(BaseModel):
    name: Optional[str] = None
    organization_id: Optional[UUID4] = None
    logo: Optional[OrganizationLogo] = None
    color_scheme: Optional[Dict[str, Any]] = None
    extra_attributes: Optional[Dict[str, Any]] = None


# Properties to receive via API on creation
class OrganizationSettingsCreate(OrganizationSettingsBase):
    name: str
    organization_id: UUID4


# Properties to receive via API on update
class OrganizationSettingsUpdate(OrganizationSettingsBase):
    pass


class OrganizationSettingsInDBBase(OrganizationSettingsBase):
    id: Optional[UUID4] = None
    creator_id: Optional[UUID4] = None
    updator_id: Optional[UUID4] = None

    class Config:
        from_attributes = True


# Additional properties to return via API
class OrganizationSettingsSchema(OrganizationSettingsInDBBase):
    pass
