from typing import List

from fastapi import APIRouter, Depends, status, Request
from pydantic import UUID4
from sqlalchemy.ext.asyncio import AsyncSession

from db.session import get_db
from domains.auth.schemas.roles import RoleCreate, RoleSchema
from domains.auth.services.role import role_service as actions

role_router = APIRouter(
    prefix="/organization/roles",
    responses={status.HTTP_404_NOT_FOUND: {"description": "Not found"}},
)


@role_router.get("/", response_model=List[RoleSchema])
# @ContentQueryChecker(roles.model.c(), None)
async def get_organization_roles(organization_id: UUID4, db: AsyncSession = Depends(get_db)):
    """Fetch all roles under a specific organization."""

    roles = await actions.list_roles(organization_id, db=db)
    return roles


# @role_router.post("/")
# async def create_role(organization_id: UUID4, request: Request, role_in: RoleCreate, db: AsyncSession = Depends(get_db)):

#     print("scheam in API: ", request.state.schema)
#     roles = await actions.create_role(organization_id, db, role_in=role_in)
#     return roles


@role_router.post("/")
async def create_role(role_in: RoleCreate, request: Request, db: AsyncSession = Depends(get_db)):
    schema = request.state.schema  # Ensure schema is extracted from request
    # print("Schema in API:", schema)

    # ✅ Ensure schema is passed when calling `create_role`
    role = await actions.create_role(schema, db, role_in=role_in)
    return role

# @role_router.post("/")
# async def create_role(organization_id: UUID4, role: RoleCreate, db: AsyncSession = Depends(get_db)):

#     get_org = await db.execute(select(Organization).where(Organization.id == organization_id))
#     get_org = get_org.scalars().first()

#     if not get_org:
#         raise HTTPException(status_code=404, detail="Organization not found")

#     schema = get_org.domain_name
#     Role.__table__.schema = schema

#     query = text(f'SELECT * FROM "{schema}".roles WHERE name = :name')
#     existing_role = await db.execute(query, {"name": role.name})

#     if existing_role.fetchone():
#         raise HTTPException(status_code=400, detail=f"'{role.name}' role already exists")

#     new_role = Role(**role.dict())
#     db.add(new_role)
#     await db.commit()

#     data = {
#         "id": new_role.id,
#         "name": new_role.name,
#         "organization": get_org,
#     }

#     return data
