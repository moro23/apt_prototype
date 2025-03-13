from db.base_class import APIBase
from sqlalchemy import Column, String, JSON, UUID, ForeignKey
from sqlalchemy.orm import relationship


class FormFieldTemplate(APIBase):
    #__table_args__ = {"schema": "public"}
    organization_id = Column(UUID(as_uuid=True), ForeignKey("public.organizations.id"))
    model_name = Column(String)
    description = Column(String, nullable=True)
    fields = Column(JSON)

    organization = relationship("Organization", back_populates="form_templates")

    def __str__(self):
        return f"{self.organization.name} {self.model_name} Fields Template"
