from sqlalchemy import Column, UUID, ForeignKey, String, JSON
from sqlalchemy.orm import relationship

from db.base_class import APIBase


class OrganizationBranch(APIBase):
    #__table_args__ = {"schema": "public"}
    organization_id = Column(
        UUID(as_uuid=True),
        ForeignKey("public.organizations.id", ondelete="CASCADE", onupdate="CASCADE"),
        nullable=False
    )
    name = Column(String, nullable=False)
    location = Column(JSON, nullable=True)  # Region/State, Town, Post_code, GPS

    organization = relationship("Organization", back_populates="branches")
    staff = relationship("Staff", foreign_keys="Staff.branch_id", back_populates="branch")
