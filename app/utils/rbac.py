from typing import Annotated

from fastapi import HTTPException, Depends, Request, status
from fastapi.security import OAuth2PasswordBearer
from jose import JWTError, jwt
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select

from config.settings import settings
from db.session import get_db
from domains.auth.models.users import User

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="auth/token")


# function to get user or User by email
async def get_user_by_email(username: str, db: AsyncSession):
    data = await db.execute(select(User).where(User.email == username))
    data = data.scalars().first()
    return data


async def get_user_by_id(id: str, db: AsyncSession):
    data = await db.execute(select(User).where(User.id == id))
    data = data.scalars().first()
    return data


async def get_all_roles(db: AsyncSession):
    data = await db.execute(select(User))
    data = data.scalars().all()
    return data


# function to get current user by token
async def get_current_user(request: Request, token: str = Depends(oauth2_scheme), db: AsyncSession = Depends(get_db)):
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials"
    )
    try:
        payload = jwt.decode(token, settings.JWT_SECRET_KEY, algorithms=[settings.ALGORITHM])
        username: str = payload.get("sub")

    except JWTError:
        raise credentials_exception
    user = await get_user_by_email(username=username, db=db)
    if user is None:
        raise credentials_exception
    return user


# function to get active current user by token
async def get_current_active_user(current_user: Annotated[User, Depends(get_current_user)]):
    if not current_user.is_active: raise HTTPException(
        status_code=status.HTTP_400_BAD_REQUEST,
        detail="you account is not active"
    )
    return current_user


# function to check if current user is super admin
async def check_if_is_system_admin(
        current_active_user: Annotated[User, Depends(get_current_user)],
        db: AsyncSession = Depends(get_db)
):
    check_system_admin = await db.execute(select(User).where(User.id == current_active_user.id))
    check_system_admin = check_system_admin.scalars().first()
    if check_system_admin.organization_id is None:
        return current_active_user

    raise HTTPException(
        status_code=status.HTTP_403_FORBIDDEN,
        detail="only system admin can access this api route"
    )
