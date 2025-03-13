from sqlalchemy import Column, String
from sqlalchemy.orm import relationship

from db.base_class import APIBase


class AppraisalTemplate(APIBase):
    name = Column(String, nullable=False)
    description = Column(String, nullable=True)
    org_type = Column(String, nullable=True)  # Private, Civil, Public, NGO

    inputs = relationship(
        "AppraisalInput",
        foreign_keys="AppraisalInput.appraisal_template_id",
        back_populates="appraisal_templates"
    )
