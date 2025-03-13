from crud.base import CRUDBase
from domains.staff.models import Department
from domains.staff.schemas.department import DepartmentCreate, DepartmentUpdate


class CRUDDepartment(CRUDBase[Department, DepartmentCreate, DepartmentUpdate]):
    pass


department_actions = CRUDDepartment(Department)
