from db.base_class import APIBase
from sqlalchemy import Column, UUID as SQLUUID, ForeignKey, Date, String
from sqlalchemy.orm import relationship


class Tenancy(APIBase):
    __table_args__ = {"schema": "public"}
    start_date = Column(Date, nullable=False)
    end_date = Column(Date, nullable=True)
    billing_cycle = Column(String, nullable=False, default="Monthly")  # Monthly, Annually
    organization_id = Column(
        SQLUUID(as_uuid=True),
        ForeignKey("public.organizations.id", ondelete="CASCADE", onupdate="CASCADE"),
        nullable=False
    )
    terms_and_conditions_id = Column(
        SQLUUID(as_uuid=True),
        ForeignKey("public.terms_and_condition.id", ondelete="CASCADE", onupdate="CASCADE")
    )
    status = Column(String, default="Active")  # Active, Terminated, Pending

    # Relationships
    organization = relationship("Organization", back_populates="tenancies")
    terms_and_conditions = relationship("TermsAndConditions", back_populates="tenancies")
    bills = relationship("Bill", back_populates="tenancy", cascade="all, delete, delete-orphan")
