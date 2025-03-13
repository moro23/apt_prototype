from sqlalchemy import Column, String, Integer, JSON, Date, UUID, ForeignKey
from sqlalchemy.orm import relationship

from db.base_class import APIBase


class Appraisal(APIBase):
    organization_id = Column(UUID(as_uuid=True), ForeignKey("public.organizations.id"))
    name = Column(String, nullable=False)
    year = Column(Integer, nullable=True)
    description = Column(String, nullable=True)
    cycle = Column(String, nullable=True)  # 'H1', 'H2', etc.
    period_from = Column(Date, nullable=True)
    period_to = Column(Date, nullable=True)

    form_fields = Column(JSON, nullable=True)

    inputs = relationship(
        "AppraisalInput", foreign_keys="AppraisalInput.appraisal_id", back_populates="appraisal"
    )
    submissions = relationship(
        "AppraisalSubmission", foreign_keys="AppraisalSubmission.appraisal_id", back_populates="appraisal"
    )
