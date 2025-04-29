from typing import Annotated
from dotenv import load_dotenv
import os

from fastapi import Depends

from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, Session
from sqlalchemy.ext.declarative import declarative_base

# Loads the information from the .env file
load_dotenv()

user = os.getenv("BD_USER")
password = os.getenv("BD_PASSWD")
host = os.getenv("BD_HOST")
port = os.getenv("BD_PORT")
schema = os.getenv("BD_SCHEMA")


# Connection to the database
SQLALCHEMY_DATABASE_URL = f'postgresql://{user}:{password}@{host}:{port}/{schema}'

engine = create_engine(SQLALCHEMY_DATABASE_URL, echo=True)

SessionLocal = sessionmaker(autocommit=False, autoflush=False,bind=engine)

base = declarative_base()

# This function automatically closes the connection
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

db_dependency = Annotated[Session, Depends(get_db)]
