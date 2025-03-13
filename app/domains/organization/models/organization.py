# import uuid
from fastapi import HTTPException
from sqlalchemy import Column, String, Boolean, Text
from sqlalchemy.dialects.postgresql import UUID as SQLUUID
from sqlalchemy.orm import relationship
from db.base_class import APIBase
from sqlalchemy.future import select

class Organization(APIBase):
    __table_args__ = {"schema": "public"}
    name = Column(String, nullable=False, unique=True)
    org_email = Column(String, nullable=False, unique=True)
    country = Column(String, nullable=False)
    org_type = Column(String, nullable=False)  # Private, Civil, Public, NGO
    is_single_branch = Column(Boolean, default=False)  # Single, Networked
    employee_range = Column(String, nullable=False)  # e.g., 0-10
    domain_name = Column(Text, nullable=False, unique=True) # gi-kace, mocd, nita, ges, gifec
    acces_url = Column(String, nullable=True) # https://moc.performance-appraisal.netlify.app
    is_active = Column(Boolean, default=True)
    subscription_plan = Column(String, nullable=False, default="Basic")  # Basic, Premium

    # Relationships
    users = relationship("User", back_populates="organization", cascade="all, delete")
    #roles = relationship("Role", back_populates="organization", cascade="all, delete")
    #files = relationship("FileUpload", back_populates="organization", cascade="all, delete")
    tenancies = relationship("Tenancy", back_populates="organization", cascade="all, delete")
    staff = relationship("Staff", back_populates="organization", cascade="all, delete-orphan")
    settings = relationship("OrganizationSettings", back_populates="organization", cascade="all, delete")
    form_templates = relationship("FormFieldTemplate", back_populates="organization", cascade="all, delete")
    branches = relationship("OrganizationBranch", back_populates="organization", cascade="all, delete")

    # Method to enforce active organization
    @staticmethod
    async def check_organization_active(org_id: SQLUUID, db):
        #organization = db.query(Organization).filter(Organization.id == org_id).first()
        existing_org = await db.execute(select(Organization).where(Organization.id == org_id))
        organization = existing_org.scalars().first()
        if not organization or not organization.is_active:
            raise HTTPException(status_code=403, detail="Organization is inactive.")

    def is_organization_active(self):
        return self.is_active

    @staticmethod
    async def toggle_active_status(org_id, new_status, db):
        """Toggle active status of an organization."""
        # organization = db.query(Organization).filter(Organization.id == org_id).first()
        existing_org = await db.execute(select(Organization).where(Organization.id == org_id))
        organization = existing_org.scalars().first()
        if not organization:
            raise HTTPException(status_code=404, detail="Organization not found.")
        organization.is_active = new_status
        db.commit()
