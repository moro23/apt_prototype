from crud.base import CRUDBase
from domains.organization.models.bill import Bill
from domains.organization.schemas.bill import (
    BillCreate, BillUpdate
)


class CRUDBill(CRUDBase[Bill, BillCreate, BillUpdate]):
    pass


bills = CRUDBill(Bill)
