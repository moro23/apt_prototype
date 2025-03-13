from typing import Dict, Any, Union, Optional
from fastapi import HTTPException, status
from fastapi.encoders import jsonable_encoder
from sqlalchemy.orm import Session
from sqlalchemy.future import select
from sqlalchemy.ext.asyncio import AsyncSession
from crud.base import CRUDBase, ModelType
from domains.auth.models.users import User
from domains.auth.schemas.user_account import (
    UserCreate, UserUpdate
)
from utils.security import pwd_context


class CRUDUser(CRUDBase[User, UserCreate, UserUpdate]):

    async def get_by_email(
            self, db: AsyncSession, *,
            email: Any,
        ) -> Optional[ModelType]:

            if id is None: 
                return None
            existing_org = await db.execute(select(self.model).where(self.model.email == email))
            existing_org = existing_org.scalars().first()

            if not existing_org:
                raise HTTPException(
                    status_code=status.HTTP_404_NOT_FOUND, detail=f"{self.model.__name__} not found"
                )
            
            return existing_org

    async def get_by_reset_password_token(self, db: Session, token: Any) -> Optional[ModelType]:
        return db.query(self.model).filter(self.model.reset_password_token == token).first()

    ## function to update admin or users password base on token after resetting password
    async def update_user_after_reset_password(
            self, db: Session, *,
            db_obj: ModelType,
            data: Union[UserUpdate, Dict[str, Any]]
    ):
        obj_data = jsonable_encoder(db_obj)
        if isinstance(data, dict):
            update_data = data
        else:
            update_data = data.model_dump(exclude_unset=True)
        for field in obj_data:
            if field in update_data:
                setattr(db_obj, field, update_data[field])
        db_obj.password = pwd_context.hash(data.password)
        db_obj.reset_password_token = None

        db.add(db_obj)
        db.flush()
        db.commit()
        db.refresh(db_obj)
        return db_obj


user_actions = CRUDUser(User)
