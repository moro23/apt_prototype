from typing import List, Optional, Literal

from sqlalchemy.orm import Session

from db.base_class import UUID
from domains.organization.repositories.organization_settings import (
    organization_settings_actions as organization_settings_repo
)
from domains.organization.schemas.organization_settings import (
    OrganizationSettingsSchema,
    OrganizationSettingsUpdate,
    OrganizationSettingsCreate
)


class OrganizationSettingsService:

    def __init__(self):
        self.repo = organization_settings_repo

    async def list_organization_setting(
            self, db: Session, *,
            skip: int = 0,
            limit: int = 100,
            order_by: str | None = None,
            order_direction: Literal['asc', 'desc'] = 'asc'
    ) -> List[OrganizationSettingsSchema]:
        organization_setting = await self.repo.get_all(
            db=db, skip=skip, limit=limit, order_by=order_by, order_direction=order_direction
        )
        return organization_setting

    async def create_organization_settings(
            self, db: Session, *, organization_settings_in: OrganizationSettingsCreate
    ) -> OrganizationSettingsSchema:
        organization_settings = await self.repo.create(db=db, data=organization_settings_in)
        return organization_settings

    async def update_organization_settings(
            self, db: Session, *, id: UUID, organization_settings_in: OrganizationSettingsUpdate
    ) -> OrganizationSettingsSchema:
        organization_settings = await self.repo.get_by_id(db=db, id=id)
        organization_settings = await self.repo.update(
            db=db, db_obj=organization_settings, data=organization_settings_in
        )
        return organization_settings

    async def get_organization_settings(self, db: Session, *, id: UUID) -> OrganizationSettingsSchema:
        organization_settings = await self.repo.get_by_id(db=db, id=id)
        return organization_settings

    async def delete_organization_settings(self, db: Session, *, id: UUID) -> None:
        await self.repo.get_by_id(db=db, id=id)
        await self.repo.remove(db=db, id=id)

    async def get_organization_settings_by_keywords(
            self, db: Session, *,
            skip: int = 0,
            limit: int = 100,
            order_by: Optional[str] = None,
            order_direction: Literal['asc', 'desc'] = 'asc',
            **kwargs
    ) -> List[OrganizationSettingsSchema]:
        organization_setting = await self.repo.get_by_filters(
            db=db, skip=skip, limit=limit, order_by=order_by, order_direction=order_direction, **kwargs
        )
        return organization_setting

    async def search_organization_setting(
            self, db: Session, *,
            skip: int = 0,
            limit: int = 100,
            order_by: Optional[str] = None,
            order_direction: Literal['asc', 'desc'] = 'asc',
            **kwargs
    ) -> List[OrganizationSettingsSchema]:
        organization_setting = await self.repo.get_by_pattern(
            db=db, skip=skip, limit=limit, order_by=order_by, order_direction=order_direction, **kwargs
        )
        return organization_setting


organization_settings_service = OrganizationSettingsService()
