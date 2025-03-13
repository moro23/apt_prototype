from typing import List, Optional, Literal

from fastapi import HTTPException
from sqlalchemy import text
from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from sqlalchemy.orm import Session

from config.logger import log
from db.base_class import UUID
from domains.auth.models.role_permissions import Role
from domains.auth.respository.role import role_actions as role_repo
from domains.auth.schemas.roles import RoleCreate, RoleUpdate, RoleSchema
from domains.organization.models import Organization


class RoleService:

    def __init__(self):
        self.repo = role_repo

    async def list_roles(self, organization_id: UUID, db: AsyncSession) -> List[RoleSchema]:
        """Fetch all roles under a specific organization and return them in the desired format."""

        org_result = await db.execute(select(Organization).where(Organization.id == organization_id))
        organization = org_result.scalars().first()
        if not organization:
            raise HTTPException(status_code=404, detail="Organization not found")

        data = await role_repo.get_by_id(db, id=organization_id)
        return data

    # async def create_role(self, organization_id: UUID4, db: Session, *, role_in: RoleCreate) -> RoleSchema:

    #     unique_fields = ["name"]

    #     role = await self.repo.create_for_tenant(db=db, data=role_in, organization_id=organization_id, unique_fields=unique_fields)
    #     return role

    async def create_role(self, schema: str, db: AsyncSession, *, role_in: RoleCreate) -> RoleSchema:
        log.debug(f"Switching schema to: {schema}")

        role = await self.repo.create(db=db, data=role_in, schema=schema, unique_fields=["name"])

        return role

    # async def create_role(self, schema: str, db: AsyncSession, roles: RoleCreate):
    #     tasks = []
    #     for role in roles:
    #         task = asyncio.create_task(self.repo.create_role(schema=schema, db=db, role_in=role))
    #         tasks.append(task)

    #     results = await asyncio.gather(*tasks, return_exceptions=True)
    #     return results

    async def update_role(self, db: Session, *, id: UUID, role_in: RoleUpdate) -> RoleSchema:
        role = await self.repo.get_by_id(db=db, id=id)
        role = await self.repo.update(db=db, db_obj=role, data=role_in)
        return role

    async def get_role(self, db: Session, *, id: UUID) -> RoleSchema:
        role = await self.repo.get_by_id(db=db, id=id)
        return role

    async def delete_role(self, db: Session, *, id: UUID) -> None:
        await self.repo.get_by_id(db=db, id=id)
        await self.repo.remove(db=db, id=id)

    async def get_role_by_keywords(
            self, db: Session, *,
            skip: int = 0,
            limit: int = 100,
            order_by: Optional[str] = None,
            order_direction: Literal['asc', 'desc'] = 'asc',
            **kwargs
    ) -> List[RoleSchema]:
        roles = await self.repo.get_by_filters(
            db=db, skip=skip, limit=limit, order_by=order_by, order_direction=order_direction, **kwargs
        )
        return roles

    async def search_roles(
            self, db: Session, *,
            skip: int = 0,
            limit: int = 100,
            order_by: Optional[str] = None,
            order_direction: Literal['asc', 'desc'] = 'asc',
            **kwargs
    ) -> List[RoleSchema]:
        roles = await self.repo.get_by_pattern(
            db=db, skip=skip, limit=limit, order_by=order_by, order_direction=order_direction, **kwargs
        )
        return roles

    async def get_user_role(self, db: AsyncSession, role_id, schema):
        try:
            # Convert role_id to UUID (ensure it's the correct type)
            role_id = UUID(role_id) if isinstance(role_id, str) else role_id

            # Set schema explicitly
            await db.execute(text(f'SET search_path TO "{schema}"'))
            log.debug(f"Schema switched to: {schema}")

            # Explicitly use the correct schema
            RoleSchema = Role.with_schema(schema)
            query = select(RoleSchema).where(RoleSchema.id == role_id)

            log.debug(f"Executing query in schema: {schema}")
            log.debug(str(query))
            log.debug("User role id:", role_id)

            # Execute the query
            result = await db.execute(query)
            user_role = result.scalars().first()

            if user_role:
                log.debug(f"User role found: {user_role.name}")
            else:
                log.debug("User role not found.")

            return user_role

        except SQLAlchemyError as e:
            log.debug(f"Database error: {e}")
            return None


role_service = RoleService()
