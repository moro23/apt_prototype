from datetime import datetime, timedelta

from db.base_class import APIBase
from sqlalchemy import Boolean, Column, DateTime, String, Integer, ForeignKey
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship


class User(APIBase):
    __table_args__ = {"schema": "public"}
    username = Column(String(255), nullable=True)
    email = Column(String(255), nullable=False)
    password = Column(String(255), nullable=True)
    reset_password_token = Column(String(255), nullable=True)
    organization_id = Column(UUID(as_uuid=True), ForeignKey('public.organizations.id'))
    role_id = Column(UUID(as_uuid=True))
    is_active = Column(Boolean, default=True)
    failed_login_attempts = Column(Integer, default=0)
    account_locked_until = Column(DateTime, nullable=True)
    lock_count = Column(Integer, default=0)

    #file_uploads = relationship("FileUpload", back_populates="users")
    organization = relationship("Organization", back_populates="users")

    def is_account_locked(self):
        return self.account_locked_until and self.account_locked_until > datetime.now()

    def lock_account(self, lock_time_minutes=10):
        self.account_locked_until = datetime.now() + timedelta(minutes=lock_time_minutes)
        self.failed_login_attempts = 0  # Reset failed attempts after locking

    def reset_failed_attempts(self):
        self.failed_login_attempts = 0
        self.account_locked_until = None
