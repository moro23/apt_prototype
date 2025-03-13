from crud.base import CRUDBase
from domains.organization.models.tenancy import Tenancy
from domains.organization.schemas.tenancy import (
    TenancyCreate, TenancyUpdate
)


class CRUDTenancy(CRUDBase[Tenancy, TenancyCreate, TenancyUpdate]):
    pass


tenancy_actions = CRUDTenancy(Tenancy)
