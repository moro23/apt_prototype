from sqlalchemy import Column, ForeignKey, UUID, JSON
from sqlalchemy.orm import relationship

from db.base_class import APIBase


class OrganizationSettings(APIBase):
    # __table_args__ = {"schema": "public"}
    organization_id = Column(UUID(as_uuid=True), ForeignKey("public.organizations.id"))
    logos = Column(JSON, nullable=True)  # Store logo paths
    color_scheme = Column(JSON, nullable=True)
    extra_attributes = Column(JSON, nullable=True)

    organization = relationship("Organization", back_populates="settings")
