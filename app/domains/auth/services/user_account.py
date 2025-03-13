from typing import List, Optional, Literal

from fastapi import HTTPException
from pydantic import UUID4
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select

from config.settings import settings
from db.base_class import UUID
from domains.auth.respository.user_account import user_actions as user_repo
from domains.auth.schemas.user_account import UserSchema, UserResponse, UserCreate, UserUpdate
from domains.auth.services.password_reset import password_reset_service
from domains.organization.models import Organization
from services.email_service import Email


class UserService:

    def __init__(self):
        self.repo = user_repo

    async def list_users(
            self,
            db: AsyncSession,
            skip: int = 0,
            limit: int = 100,
            order_by: str | None = None,
            order_direction: Literal['asc', 'desc'] = 'asc'
    ) -> UserResponse:
        users = await self.repo.get_all(
            db=db, skip=skip, limit=limit,
            order_by=order_by, order_direction=order_direction
        )
        return users

    async def create_user(self, organization_id: UUID4, user_in: UserCreate, db: AsyncSession) -> UserSchema:
        """Creates a new user under an organization and returns the user with role details."""

        get_org = await db.execute(select(Organization).where(Organization.id == organization_id))
        get_org = get_org.scalars().first()

        if not get_org:
            raise HTTPException(status_code=404, detail="Organization not found")

        unique_fields = ["email"]

        user_db = await self.repo.create(db=db, data=user_in, unique_fields=unique_fields)

        token = await password_reset_service.generate_reset_token()
        user_db.reset_password_token = token
        await db.commit()
        #  Send email with the reset link
        reset_link = f"{settings.FRONTEND_URL}/login/resetpassword?token={token}"

        from domains.auth.apis.login import send_reset_email

        email_data = await send_reset_email(user_in.username, user_in.email, reset_link)
        await Email.sendMailService(email_data, template_name='password_reset.html')
        return user_db

    async def update_user(self, db: AsyncSession, *, id: UUID, user_in: UserUpdate) -> UserSchema:
        user = await self.repo.get_by_id(db=db, id=id)
        user = await self.repo.update(db=db, db_obj=user, data=user_in)
        return user

    async def get_user(self, db: AsyncSession, *, id: UUID) -> UserSchema:
        user = await self.repo.get_by_id(db=db, id=id)
        return user

    async def delete_user(self, db: AsyncSession, *, id: UUID) -> None:
        await self.repo.get_by_id(db=db, id=id)
        await self.repo.remove(db=db, id=id)

    async def get_user_by_keywords(
            self, db: AsyncSession, *,
            skip: int = 0,
            limit: int = 100,
            order_by: Optional[str] = None,
            order_direction: Literal['asc', 'desc'] = 'asc',
            **kwargs
    ) -> List[UserSchema]:
        users = await self.repo.get_by_filters(
            db=db, skip=skip, limit=limit, order_by=order_by, order_direction=order_direction, **kwargs
        )
        return users

    async def search_users(
            self, db: AsyncSession, *,
            skip: int = 0,
            limit: int = 100,
            order_by: Optional[str] = None,
            order_direction: Literal['asc', 'desc'] = 'asc',
            **kwargs
    ) -> List[UserSchema]:
        users = await self.repo.get_by_pattern(
            db=db, skip=skip, limit=limit, order_by=order_by, order_direction=order_direction, **kwargs
        )
        return users


users_forms_service = UserService()
