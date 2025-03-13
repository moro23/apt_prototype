from typing import Optional

from crud.base import CRUDBase
from domains.appraisal.models.appraisal import Appraisal
from domains.appraisal.schemas.appraisal import AppraisalCreate, AppraisalUpdate
from pydantic import UUID4
from sqlalchemy.orm import Session


class CRUDAppraisal(CRUDBase[Appraisal, AppraisalCreate, AppraisalUpdate]):
    async def get(self, db: Session, id: UUID4) -> Optional[Appraisal]:
        return (
            db.query(Appraisal)
            .join(Appraisal.inputs)
            .filter(Appraisal.id == id)
            .first()
        )


appraisal_actions = CRUDAppraisal(Appraisal)
