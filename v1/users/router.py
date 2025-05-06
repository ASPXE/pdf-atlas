from fastapi import APIRouter, Depends
from v1.auth.router import get_current_user


users_router = APIRouter(
    prefix="/users",
    tags=["Users"],
    responses={404: {"description": "Users router not found"}},
    dependencies=[Depends(get_current_user)]
)

@users_router.get("/greetings")
async def greetings():
    return {"message": "Welcome to the Users endpoint!"}

# TODO: Create the endpoints to edit the email and password. 
