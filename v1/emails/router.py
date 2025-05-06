from fastapi import APIRouter, Depends
from v1.auth.router import get_current_user

emails_router = APIRouter(
    prefix="/emails",
    tags=["Emails"],
    responses={404: {"description":"Emails not found"}},
    dependencies=[Depends(get_current_user)]
)

@emails_router.get("/greetings")
async def greetings():
    return {"message":"Hello from emails endpoint"}