from crud.base import CRUDBase
from domains.staff.models import Staff
from domains.staff.schemas.staff import StaffCreate, StaffUpdate


class CRUDStaff(CRUDBase[Staff, StaffCreate, StaffUpdate]):
    pass


staff_actions = CRUDStaff(Staff)
