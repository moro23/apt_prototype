from crud.base import CRUDBase
from domains.appraisal.models.department_group import DepartmentGroup
from domains.appraisal.schemas.department_group import (
    DepartmentGroupCreate, DepartmentGroupUpdate
)


class CRUDDepartmentGroup(CRUDBase[DepartmentGroup, DepartmentGroupCreate, DepartmentGroupUpdate]):
    pass


department_group_actions = CRUDDepartmentGroup(DepartmentGroup)
