from db.base_class import APIBase, UUID
from sqlalchemy import Column, ForeignKey, String
from sqlalchemy.orm import relationship


class DepartmentGroup(APIBase):
    department_id = Column(UUID, ForeignKey("departments.id"), nullable=True)
    name = Column(String)
    #
    department = relationship("Department", back_populates="groups")
    appraisal_inputs = relationship(
        "AppraisalInput", foreign_keys="AppraisalInput.department_group_id", back_populates="department_group"
    )
