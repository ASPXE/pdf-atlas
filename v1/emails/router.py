from fastapi import APIRouter


emails_router = APIRouter(
    prefix="/emails",
    tags=["Emails"],
    responses={404: {"description":"Emails not found"}}
)

@emails_router.get("/greetings")
async def greetings():
    return {"message":"Hello from emails endpoint"}