from db.base_class import APIBase
from sqlalchemy import Column, UUID as SQLUUID, ForeignKey, DECIMAL, Date, String
from sqlalchemy.orm import relationship


class Bill(APIBase):
    __table_args__ = {"schema": "public"}
    tenancy_id = Column(
        SQLUUID(as_uuid=True),
        ForeignKey("public.tenancies.id", ondelete="CASCADE", onupdate="CASCADE"),
        nullable=False
    )
    amount = Column(DECIMAL(precision=10, scale=2), nullable=False)
    due_date = Column(Date, nullable=False)
    status = Column(String, default="Unpaid")  # Unpaid, Paid, Overdue

    # Relationships
    tenancy = relationship("Tenancy", back_populates="bills")
    payments = relationship("Payment", back_populates="bill", cascade="all, delete, delete-orphan")
