from datetime import datetime

from fastapi import Depends, HTTPException, status, Response, Request
from jose import JWTError
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select

from config.logger import log
from db.session import get_db
from domains.auth.models.refresh_token import RefreshToken
from domains.auth.services import login as loginService
from domains.auth.services.user_account import users_forms_service
from utils.security import Security


async def logout_user(request: Request, response: Response, db: AsyncSession = Depends(get_db)):
    tokens = await loginService.get_tokens(request)
    if not tokens['AccessToken'] or not tokens['RefreshToken']: raise HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="No token provided"
    )

    # Verify the refresh token
    try:
        payload = Security.decode_token(tokens['AccessToken'])
        user_email = payload.get("sub")
    except JWTError:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid tokens"
        )

    if not user_email: raise HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Unable to determine logged-in user"
    )

    log.debug(f"email from payload token: {user_email}")
    # Retrieve the user's refresh token
    user = await users_forms_service.repo.get_by_email(db=db, email=user_email)
    if not user: raise HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="User not found"
    )

    refresh_token = await db.execute(select(RefreshToken).where(RefreshToken.user_id == user.id))
    refresh_token = refresh_token.scalars().first()
    # refresh_token = db.query(RefreshToken).filter(RefreshToken.user_id == user.id).first()
    if not refresh_token: raise HTTPException(
        status_code=status.HTTP_404_NOT_FOUND,
        detail="Refresh token not found"
    )

    # Invalidate the token by setting the logged_out_at timestamp
    refresh_token.logged_out_at = datetime.now()
    await db.delete(refresh_token)
    await db.commit()

    # Clear tokens from the cookies
    response.delete_cookie(key="AccessToken")
    response.delete_cookie(key="RefreshToken")

    return {"status": "logged out successfully"}
