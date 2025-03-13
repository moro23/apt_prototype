from db.base_class import APIBase
from sqlalchemy import Column, String, JSON
from sqlalchemy.orm import relationship


class Department(APIBase):
    name = Column(String, nullable=False)
    form_fields = Column(JSON, nullable=False)  # JSON field to store form fields configuration

    staff = relationship("Staff", back_populates="department")
    groups = relationship("DepartmentGroup", back_populates="department", cascade="all, delete")

    def str(self):
        return f"{self.name}"
