from fastapi import APIRouter, Depends, HTTPException
from fastapi.security import OAuth2PasswordRequestForm, OAuth2PasswordBearer
from v1.bd.database import db_dependency
from v1.users.models import CreateUserRequest, Users
from datetime import datetime, timezone, timedelta
from http import HTTPStatus
from http.client import HTTPResponse
from typing import Annotated
from v1.auth.models import Token
import os
from dotenv import load_dotenv
from passlib.context import CryptContext
from starlette import status # Returns the HTPP Responses
from jose import jwt, JWTError

# Loads the data fron .env file
load_dotenv()

ALGORITHM = os.getenv("ALGORITHM")
SECRET = os.getenv("SECRET")
ACCESS_TOKEN_EXPIRE_MINUTES = 20 # 20 minutes

bcrypt_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

# Each endpoint must have this dependency to check if the token is valid
oauth2_bearer = OAuth2PasswordBearer(tokenUrl='auth/token')

auth_router = APIRouter(
    prefix="/auth",
    tags=["Auth"],
    responses={404: {"description": "Auth router not found"}}
)


@auth_router.get("/greetings")
async def greetings():
    return {"message": "Welcome to auth router!"}

@auth_router.post("/sign-up", status_code=status.HTTP_201_CREATED)
async def sign_up(db: db_dependency, create_user_form: CreateUserRequest):

    create_user_model = Users(
        passwd_auth = bcrypt_context.hash(create_user_form.passwd_auth), # Hashes the password
        email = create_user_form.email,
        creation_date = datetime.now(timezone.utc),
        validation_date = None, # All new Users are not validated
        is_active = True # All new accounts are active
    )    

    db.add(create_user_model)
    db.commit()

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


def authenticate_user(db: db_dependency, email: str, passwd_auth: str):
    user = db.query(Users).filter(Users.email == email).first()
    if not user:
        return False
    if not bcrypt_context.verify(passwd_auth, user.passwd_auth):
        return False
    return user  

async def get_current_user(token: Annotated[str, Depends(oauth2_bearer)]):
    try:
        payload = jwt.decode(token, SECRET, algorithms=[ALGORITHM])
        username: str = payload.get('sub') # email
        user_id: int = payload.get('id') # id_users
        if username is None or user_id is None:
            raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED,
                                detail='Credentials not validated')
        return {'username': username, 'id': user_id}
    except JWTError:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED,
                            detail='Credentials not validated')

# Endpoint that sends the auth token and validates the user
@auth_router.post("/token", response_model=Token)
async def token(form_data: Annotated[OAuth2PasswordRequestForm, Depends()], db: db_dependency):

    user = authenticate_user(db, form_data.email, form_data.passwd_auth)

    if not user:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED,
                            detail='Credentials not validated')

    token = create_access_token(user.email, user.id_users, timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES))

    return {'access_token': token, 'token_type': 'Bearer'}

