from sqlalchemy import Column, ForeignKey, String, Table
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship

from db.base_class import APIBase

# Define the association table with explicit schema reference
role_permissions = Table(
    'role_permissions',
    APIBase.metadata,
    Column('role_id', UUID(as_uuid=True), ForeignKey('roles.id'), primary_key=True),
    Column('permission_id', UUID(as_uuid=True), ForeignKey('permissions.id'), primary_key=True),
    schema="public"  # Explicitly set schema
)


class Role(APIBase):
    # __tablename__ = 'roles'
    # __table_args__ = {'schema': 'public'}  # Dynamically assign schema.

    name = Column(String(255), unique=True)
    # organization_id = Column(UUID(as_uuid=True), ForeignKey('organizations.id'))
    # organization = relationship("Organization", back_populates="roles")
    permissions = relationship(
        "Permission",
        secondary=role_permissions,
        back_populates="roles"
    )

    @classmethod
    def with_schema(cls, schema_name):
        """Dynamically assign schema."""
        cls.__table__.schema = schema_name
        return cls


class Permission(APIBase):
    # __tablename__ = 'permissions'

    name = Column(String(255), unique=True)
    roles = relationship(
        "Role",
        secondary=role_permissions,
        back_populates="permissions"
    )
