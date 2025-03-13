from crud.base import CRUDBase
from domains.auth.models.role_permissions import Role
from domains.auth.schemas.roles import (
    RoleCreate, RoleUpdate
)


class CRUDRole(CRUDBase[Role, RoleCreate, RoleUpdate]):
    pass


role_actions = CRUDRole(Role)
