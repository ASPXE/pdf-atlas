from fastapi import APIRouter


users_router = APIRouter(
    prefix="/users",
    tags=["Users"],
    responses={404: {"description": "Users router not found"}}
)

@users_router.get("/greetings")
async def greetings():
    return {"message": "Welcome to the Users endpoint!"}