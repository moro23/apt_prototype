from fastapi import APIRouter

from services.email_service import EmailSchema, Email

email_router = APIRouter(
    responses={404: {"description": "Not found"}},
)


## Endpoint for sending email aynchronously 
@email_router.post("/send_email")
async def send_email_async(data: EmailSchema):
    return await Email.sendMailService(data, template_name="welcome_email.html")
