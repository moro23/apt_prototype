from crud.base import CRUDBase
from domains.organization.models.payment import Payment
from domains.organization.schemas.payment import (
    PaymentCreate, PaymentUpdate
)


class CRUDPayment(CRUDBase[Payment, PaymentCreate, PaymentUpdate]):
    pass


payment_actions = CRUDPayment(Payment)
