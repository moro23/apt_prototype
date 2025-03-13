from typing import Any, List, Literal

from fastapi import APIRouter, Depends, status, Request
from fastapi import HTTPException
from fastapi.responses import JSONResponse
from pydantic import UUID4
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import Session

from config.settings import settings
from db.session import get_db
from domains.auth.apis.login import send_reset_email
from domains.auth.models.users import User
from domains.auth.schemas import user_account as schemas
from domains.auth.schemas.password_reset import ResetPasswordRequest
from domains.auth.services.password_reset import password_reset_service
from domains.auth.services.user_account import users_forms_service as actions
from services.email_service import Email
from utils.rbac import check_if_is_system_admin
from utils.schemas import HTTPError

users_router = APIRouter(
    responses={404: {"description": "Not found"}},
)


# @users_router.post("/users/")
# async def create_user(user: schemas.UserCreate, request: Request, db: AsyncSession = Depends(get_db)):
#     schema = request.state.schema

#     if not schema:
#         raise HTTPException(status_code=400, detail="Schema not found")

#     User.__table__.schema = schema  

#     new_user = User(**user.dict())
#     db.add(new_user)
#     await db.commit()

#     return {"message": "User created successfully in schema " + schema}


@users_router.get(
    "/",
    response_model=List[schemas.UserSchema]
)
# @ContentQueryChecker(users.model.c(), None)
async def list_users(request: Request,
                     db: AsyncSession = Depends(get_db),
                     skip: int = 0,
                     limit: int = 100,
                     order_by: str | None = None,
                     order_direction: Literal['asc', 'desc'] = 'asc'
                     ) -> Any:
    users = await actions.list_users(
        db=db, skip=skip, limit=limit, order_by=order_by, order_direction=order_direction
    )
    schema = request.state.schema
    print("schema: {}".format(schema))
    return users


@users_router.post(
    "/",
    response_model=schemas.UserSchema,
    status_code=status.HTTP_201_CREATED
)
async def create_user(
        *,
        organization_id: UUID4,
        user_in: schemas.UserCreate,
        db: Session = Depends(get_db)
) -> Any:
    user = await actions.create_user(organization_id, user_in, db)
    return user


@users_router.put(
    "/{id}",
    response_model=schemas.UserSchema,
    responses={status.HTTP_404_NOT_FOUND: {"model": HTTPError}},
)
async def update_user(
        *, db: Session = Depends(get_db),
        current_user: User = Depends(check_if_is_system_admin),
        id: UUID4,
        user_in: schemas.UserUpdate,
) -> Any:
    user = await actions.update_user(db=db, id=id, user_in=user_in)
    return user


@users_router.get(
    "/{id}",
    response_model=schemas.UserSchema
)
async def get_user(
        *, db: Session = Depends(get_db),
        current_user: User = Depends(check_if_is_system_admin),
        id: UUID4
) -> Any:
    user = await actions.get_user(db=db, id=id)
    return user


@users_router.delete(
    "/{id}",
    response_model=schemas.UserSchema
)
async def delete_user(
        *, db: Session = Depends(get_db),
        current_user: User = Depends(check_if_is_system_admin),
        id: UUID4
) -> None:
    await actions.delete_user(db=db, id=id)


@users_router.post(
    "/forgot_password/"
)
async def request_password_reset(
        *, db: Session = Depends(get_db),
        reset_password_request: ResetPasswordRequest,
):
    user = await actions.repo.get_by_email(db=db, email=reset_password_request.email, silent=False)

    token = await password_reset_service.generate_reset_token()
    user.reset_password_token = token
    db.commit()

    reset_link = f"{settings.FRONTEND_URL}/login/resetpassword?token={token}"
    email_data = await send_reset_email(user.username, user.email, reset_link)

    await Email.sendMailService(email_data, template_name='forgot-password.html')
    return JSONResponse(content={"message": "Password reset link has been sent to your email."}, status_code=200)


@users_router.put(
    "/reset_password_token/{token}",
    response_model=schemas.UserSchema
)
async def update_user_with_reset_password_token(
        *, db: Session = Depends(get_db),
        token: str,
        data: schemas.UpdatePassword
):
    update_user = await actions.repo.get_by_reset_password_token(db=db, token=token)
    if not update_user: raise HTTPException(
        status_code=status.HTTP_404_NOT_FOUND, detail="Invalid Token"
    )
    data = await actions.repo.users_form_repo.update_user_after_reset_password(db=db, db_obj=update_user, data=data)
    return data
