from crud.base import CRUDBase
from domains.organization.models.terms_and_conditions import TermsAndConditions
from domains.organization.schemas.terms_and_conditions import (
    TermsAndConditionsCreate, TermsAndConditionsUpdate
)


class CRUDTermsAndConditions(CRUDBase[TermsAndConditions, TermsAndConditionsCreate, TermsAndConditionsUpdate]):
    pass


terms_and_conditions = CRUDTermsAndConditions(TermsAndConditions)
