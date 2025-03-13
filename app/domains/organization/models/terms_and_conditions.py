from db.base_class import APIBase
from sqlalchemy import Column, String, Boolean
from sqlalchemy.dialects.postgresql import JSONB
from sqlalchemy.orm import relationship


class TermsAndConditions(APIBase):
    __table_args__ = {"schema": "public"}
    title = Column(String, nullable=False)
    content = Column(JSONB, nullable=False)  # Flexibility for dynamic content  # Store T&Cs as JSON for flexibility
    version = Column(String, nullable=True, unique=True)  # For historical tracking
    is_active = Column(Boolean, default=True)

    # Relationships
    tenancies = relationship("Tenancy", back_populates="terms_and_conditions")
