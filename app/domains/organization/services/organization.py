from typing import List, Literal

from fastapi import HTTPException, Depends
from sqlalchemy import text
from sqlalchemy.ext.asyncio import async_sessionmaker, AsyncSession
from sqlalchemy.future import select

from db.base_class import UUID
from db.session import get_db, engine
from domains.organization.models import Organization
from domains.organization.repositories.organization import organizations as organization_repo
from domains.organization.schemas.organization import (RoleSchema,
OrganizationWithUsersResponse,
OrganizationUpdate,
OrganizationCreate, OrganizationWithUsersResponse, UserResponse,
OrganizationSchema)

AsyncSessionLocal = async_sessionmaker(engine, expire_on_commit=False)


class OrganizationService:

    def __init__(self):
        self.repo = organization_repo

    async def create_organization(
            self, *, data: OrganizationCreate, db: AsyncSession = Depends(get_db)
    ) -> OrganizationSchema:

        unique_fields = ["name", "org_email", "domain_name"]

        new_org_public = await organization_repo.create(db=db, data=data, unique_fields=unique_fields)
        await organization_repo.create_schema(domain_name=data.domain_name, db=db)
        return new_org_public

    async def list_organizations(
            self,
            db: AsyncSession,
            skip: int = 0,
            limit: int = 100,
            order_by: str | None = None,
            order_direction: Literal['asc', 'desc'] = 'asc'
    ) -> List[OrganizationSchema]:
        """Fetch all organizations."""

        organizations = await organization_repo.get_all(
            db=db, skip=skip, limit=limit,
            order_by=order_by, order_direction=order_direction
        )
        return organizations

    async def update_organization(
            self,
            *,
            id: UUID,
            data: OrganizationUpdate,
            db: AsyncSession
    ) -> OrganizationSchema:

        unique_fields = ["name", "org_email", "domain_name"]
        updated_org = await organization_repo.update(db=db, id=id, data=data, unique_fields=unique_fields)
        return updated_org

    async def get_organization(self, db: AsyncSession, *, id: UUID) -> OrganizationWithUsersResponse:
        """Fetch a specific organization with its users and their roles, 
        and return the response wrapped with bk_size, pg_size and data keys."""

        result = await db.execute(select(Organization).where(Organization.id == id))
        organization = result.scalars().first()
        if not organization:
            raise HTTPException(status_code=404, detail="Organization not found")

        schema = organization.domain_name

        users_query = text('SELECT * FROM public.users WHERE organization_id = :organization_id')
        users_result = await db.execute(users_query, {"organization_id": str(id)})
        users = users_result.mappings().all()

        get_org_roles = text(f'SELECT * FROM "{schema}".roles')
        roles_result = await db.execute(get_org_roles)
        roles = roles_result.mappings().all()

        users_list = []
        role_list = []
        for user in users:
            role_query = text(f'SELECT * FROM "{schema}".roles WHERE id = :role_id')
            role_result = await db.execute(role_query, {"role_id": str(user["role_id"])})
            role = role_result.mappings().first()

            role_data = (
                RoleSchema(id=user["role_id"], name=role["name"])
                if role else None
            )

            users_list.append(
                UserResponse(
                    id=user["id"],
                    username=user["username"],
                    email=user["email"],
                    role=role_data,
                )
            )

        for role in roles:
            role_data = (
                RoleSchema(id=role["id"], name=role["name"])
                if role else None
            )

            role_list.append(
                RoleSchema(id=role["id"], name=role["name"])
            )

        return OrganizationWithUsersResponse(
                    id=organization.id,
                    name=organization.name,
                    org_email=organization.org_email,
                    country=organization.country,
                    org_type=organization.org_type,
                    is_single_branch=organization.is_single_branch,
                    employee_range=organization.employee_range,
                    domain_name=organization.domain_name,
                    is_active=organization.is_active,
                    subscription_plan=organization.subscription_plan,
                    users=users_list,
                    roles=role_list
        )

    async def delete_organization(
            self,
            *,
            id: UUID,
            db: AsyncSession,
            soft_delete: bool
    ) -> OrganizationSchema:
        """
        Soft-delete an organization by setting is_deleted to True, is_active to False,
        and deleted_at to the current timestamp.
        """
        delete_organization = await organization_repo.delete(db=db, id=id, soft=soft_delete)
        return delete_organization

    async def reactivate_organization(
            self,
            *,
            id: UUID,
            db: AsyncSession
    ) -> OrganizationSchema:
        reactivate = await organization_repo.reactivate(db=db, id=id)
        return reactivate


organization_service = OrganizationService()
