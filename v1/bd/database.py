from dotenv import load_dotenv
import os
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession, async_sessionmaker
from sqlalchemy.ext.declarative import declarative_base
from typing import AsyncGenerator

# Load .env values
load_dotenv()

user = os.getenv("BD_USER")
password = os.getenv("BD_PASSWD")
host = os.getenv("BD_HOST")
port = os.getenv("BD_PORT")
schema = os.getenv("BD_SCHEMA")

# ✔ Use async PostgreSQL driver
SQLALCHEMY_DATABASE_URL = f"postgresql+asyncpg://{user}:{password}@{host}:{port}/{schema}"

# ✔ Create async engine and session
engine = create_async_engine(SQLALCHEMY_DATABASE_URL, echo=True)
async_session = async_sessionmaker(engine, expire_on_commit=False, class_=AsyncSession)

# Base for models
base = declarative_base()

# ✔ Dependency function
async def get_db() -> AsyncGenerator[AsyncSession, None]:
    async with async_session() as session:
        yield session
