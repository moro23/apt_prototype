from crud.base import CRUDBase
from domains.organization.models.organization import Organization
from domains.organization.schemas.organization import (
    OrganizationCreate, OrganizationUpdate
)


class CRUDOrganization(CRUDBase[Organization, OrganizationCreate, OrganizationUpdate]):
    pass


organizations = CRUDOrganization(Organization)
