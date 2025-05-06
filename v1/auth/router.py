from fastapi import APIRouter, Depends, HTTPException
from fastapi.security import OAuth2PasswordRequestForm, OAuth2PasswordBearer
from v1.bd.database import get_db
from v1.users.models import CreateUserRequest, Users
from datetime import datetime, timezone, timedelta
from typing import Annotated
from v1.auth.models import Token
import os
from dotenv import load_dotenv
from passlib.context import CryptContext
from starlette import status  # Returns the HTTP Responses
from jose import jwt, JWTError
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select

# Loads the data from .env file
load_dotenv()

ALGORITHM = os.getenv("ALGORITHM")
SECRET = os.getenv("SECRET")
ACCESS_TOKEN_EXPIRE_MINUTES = 20  # 20 minutes

bcrypt_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

# OAuth2PasswordBearer for token retrieval
oauth2_bearer = OAuth2PasswordBearer(tokenUrl='v1/auth/token')

auth_router = APIRouter(
    prefix="/auth",
    tags=["Auth"],
    responses={404: {"description": "Auth router not found"}}
)


@auth_router.get("/greetings")
async def greetings():
    return {"message": "Welcome to auth router!"}


# Function to check if the email is available
async def check_available_email(db: AsyncSession, email: str) -> bool:
    stmt = select(Users).where(Users.email == email)
    result = await db.execute(stmt)
    user = result.scalar_one_or_none()
    return user is None


# Sign-up endpoint
@auth_router.post("/sign-up", status_code=status.HTTP_201_CREATED)
async def sign_up(
    create_user_form: CreateUserRequest,  # Receive the data as CreateUserRequest
    db: AsyncSession = Depends(get_db)  # Inject db session
):
    # Check if the email is available
    is_available = await check_available_email(db, create_user_form.email)

    if not is_available:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="Email is already taken"
        )

    # Create the new user
    new_user = Users(
        passwd_auth=bcrypt_context.hash(create_user_form.passwd_auth),  # Hash password
        email=create_user_form.email,
        creation_date=datetime.now(timezone.utc),
        validation_date=None,
        is_active=True
    )

    db.add(new_user)
    await db.commit()
    await db.refresh(new_user)

    return {"message": "User created successfully", "user": new_user}


def create_access_token(email: str, id_users: int, expires_delta: timedelta):
    # Data to hash the token
    encode = {'sub': email, 'id': id_users}

    # Calculates expiration date
    if expires_delta:
        expire = datetime.now(timezone.utc) + expires_delta
    else:
        expire = datetime.now(timezone.utc) + timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)

    # Adds expiration date to the hashed data
    encode.update({'exp': expire})

    # Encodes the token
    return jwt.encode(encode, SECRET, algorithm=ALGORITHM)


def authenticate_user(db: AsyncSession, email: str, passwd_auth: str):
    stmt = select(Users).filter(Users.email == email)
    result = db.execute(stmt)
    user = result.scalar_one_or_none()
    
    if not user:
        return False
    if not bcrypt_context.verify(passwd_auth, user.passwd_auth):
        return False
    return user


# Current user validation (decoding the token)
async def get_current_user(token: Annotated[str, Depends(oauth2_bearer)]):
    try:
        payload = jwt.decode(token, SECRET, algorithms=[ALGORITHM])
        username: str = payload.get('sub')  # email
        user_id: int = payload.get('id')  # id_users
        if username is None or user_id is None:
            raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED,
                                detail='Credentials not validated')
        return {'username': username, 'id': user_id}
    except JWTError:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED,
                            detail='Credentials not validated')


# Endpoint that sends the auth token and validates the user
@auth_router.post("/token", response_model=Token)
async def token(form_data: Annotated[OAuth2PasswordRequestForm, Depends()], db: AsyncSession = Depends(get_db)):
    user = await authenticate_user(db, form_data.username, form_data.password)

    if not user:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED,
                            detail='Credentials not validated')

    token = create_access_token(
        email=user.email,
        id_users=user.id_users,
        expires_delta=timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    )

    return {'access_token': token, 'token_type': 'Bearer'}

