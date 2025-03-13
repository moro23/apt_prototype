from db.base_class import APIBase
from sqlalchemy import (
    Column, ForeignKey, UUID, JSON
)
from sqlalchemy.orm import relationship


class Staff(APIBase):
    organization_id = Column(UUID(as_uuid=True), ForeignKey("public.organizations.id"))
    department_id = Column(UUID(as_uuid=True), ForeignKey("departments.id"))
    user_id = Column(UUID(as_uuid=True), ForeignKey("public.users.id"))
    branch_id = Column(UUID(as_uuid=True), ForeignKey("organization_branches.id"))

    form_fields = Column(JSON, nullable=False)  # JSON field to store form fields configuration

    user = relationship("User", foreign_keys="Staff.user_id")
    branch = relationship("OrganizationBranch", foreign_keys="Staff.branch_id", back_populates="staff")
    department = relationship("Department", back_populates="staff")
    appraisal_submissions = relationship(
        "AppraisalSubmission", foreign_keys="AppraisalSubmission.staff_id", back_populates="staff"
    )
    organization = relationship("Organization", back_populates="staff")
