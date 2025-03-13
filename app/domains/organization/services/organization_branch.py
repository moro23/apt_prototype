from typing import List, Optional, Literal

from sqlalchemy.orm import Session

from db.base_class import UUID
from domains.organization.repositories.organization_branch import (
    organization_branch_actions as organization_branch_repo
)
from domains.organization.schemas.organization_branch import (
    OrganizationBranchSchema,
    OrganizationBranchUpdate,
    OrganizationBranchCreate
)


class OrganizationBranchService:

    def __init__(self):
        self.repo = organization_branch_repo

    async def list_organization_branches(
            self, db: Session, *,
            skip: int = 0,
            limit: int = 100,
            order_by: str | None = None,
            order_direction: Literal['asc', 'desc'] = 'asc'
    ) -> List[OrganizationBranchSchema]:
        organization_branches = await self.repo.get_all(
            db=db, skip=skip, limit=limit, order_by=order_by, order_direction=order_direction
        )
        return organization_branches

    async def create_organization_branch(
            self, db: Session, *, organization_branch_in: OrganizationBranchCreate
    ) -> OrganizationBranchSchema:
        organization_branch = await self.repo.create(db=db, data=organization_branch_in)
        return organization_branch

    async def update_organization_branch(
            self, db: Session, *, id: UUID, organization_branch_in: OrganizationBranchUpdate
    ) -> OrganizationBranchSchema:
        organization_branch = await self.repo.get_by_id(db=db, id=id)
        organization_branch = await self.repo.update(db=db, db_obj=organization_branch, data=organization_branch_in)
        return organization_branch

    async def get_organization_branch(self, db: Session, *, id: UUID) -> OrganizationBranchSchema:
        organization_branch = await self.repo.get_by_id(db=db, id=id)
        return organization_branch

    async def delete_organization_branch(self, db: Session, *, id: UUID) -> None:
        await self.repo.get_by_id(db=db, id=id)
        await self.repo.remove(db=db, id=id)

    async def get_organization_branch_by_keywords(
            self, db: Session, *,
            skip: int = 0,
            limit: int = 100,
            order_by: Optional[str] = None,
            order_direction: Literal['asc', 'desc'] = 'asc',
            **kwargs
    ) -> List[OrganizationBranchSchema]:
        organization_branches = await self.repo.get_by_filters(
            db=db, skip=skip, limit=limit, order_by=order_by, order_direction=order_direction, **kwargs
        )
        return organization_branches

    async def search_organization_branches(
            self, db: Session, *,
            skip: int = 0,
            limit: int = 100,
            order_by: Optional[str] = None,
            order_direction: Literal['asc', 'desc'] = 'asc',
            **kwargs
    ) -> List[OrganizationBranchSchema]:
        organization_branches = await self.repo.get_by_pattern(
            db=db, skip=skip, limit=limit, order_by=order_by, order_direction=order_direction, **kwargs
        )
        return organization_branches


organization_branch_service = OrganizationBranchService()
