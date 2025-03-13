from crud.base import CRUDBase
from domains.organization.models.organization_branch import OrganizationBranch
from domains.organization.schemas.organization_branch import (
    OrganizationBranchCreate, OrganizationBranchUpdate
)


class CRUDOrganizationBranch(CRUDBase[OrganizationBranch, OrganizationBranchCreate, OrganizationBranchUpdate]):
    pass


organization_branch_actions = CRUDOrganizationBranch(OrganizationBranch)
