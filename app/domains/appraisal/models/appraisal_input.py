from db.base_class import APIBase, UUID
from sqlalchemy import Column, ForeignKey, JSON, Boolean
from sqlalchemy.dialects.postgresql import JSONB
from sqlalchemy.orm import relationship


class AppraisalInput(APIBase):
    organization_id = Column(UUID(as_uuid=True), ForeignKey("public.organizations.id"))
    appraisal_id = Column(UUID, ForeignKey("appraisals.id"))
    appraisal_template_id = Column(UUID, ForeignKey("appraisal_templates.id"))
    department_group_id = Column(UUID, ForeignKey("department_groups.id"))
    department_ids = Column(JSONB, nullable=True)  # List of department IDs targeted

    form_fields = Column(JSON, nullable=False)  # JSON field to store form fields configuration

    submitted = Column(Boolean, default=False)
    completed = Column(Boolean, default=False)
    is_global = Column(Boolean, default=False)
    is_active = Column(Boolean, default=False)
    #
    appraisal = relationship(
        "Appraisal", foreign_keys="AppraisalInput.appraisal_id", back_populates="inputs"
    )
    appraisal_templates = relationship(
        "AppraisalTemplate", foreign_keys="AppraisalInput.appraisal_template_id", back_populates="inputs"
    )
    department_group = relationship(
        "DepartmentGroup", foreign_keys="AppraisalInput.department_group_id", back_populates="appraisal_inputs"
    )
    #
    submissions = relationship(
        "AppraisalSubmission", foreign_keys="AppraisalSubmission.appraisal_input_id", back_populates="appraisal_input"
    )
