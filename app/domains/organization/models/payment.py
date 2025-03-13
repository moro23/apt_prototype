from db.base_class import APIBase
from sqlalchemy import Column, UUID as SQLUUID, ForeignKey, DECIMAL, DateTime, func, String
from sqlalchemy.orm import relationship


class Payment(APIBase):
    __table_args__ = {"schema": "public"}
    bill_id = Column(
        SQLUUID(as_uuid=True),
        ForeignKey("public.bills.id", ondelete="CASCADE", onupdate="CASCADE"),
        nullable=False
    )
    amount_paid = Column(DECIMAL(precision=10, scale=2), nullable=False)
    payment_date = Column(DateTime(timezone=True), default=func.now())
    payment_method = Column(String, nullable=False)  # Card, Bank Transfer, Mobile Money
    transaction_id = Column(String, unique=True, nullable=False)
    status = Column(String, default="Success")  # Success, Failed, Pending

    # Relationships
    bill = relationship("Bill", back_populates="payments")
