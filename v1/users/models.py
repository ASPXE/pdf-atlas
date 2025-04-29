from pydantic import BaseModel
from sqlalchemy import Column, Text, Integer, TIMESTAMP, Boolean
from datetime import datetime
from typing import Optional
from v1.bd.database import base

# This class is used by SQLAlchemy
class Users(base):

    __tablename__ = "users"

    id_users: int = Column(Integer, primary_key=True, index=True)
    email: str = Column(Text, nullable=False)
    passwd_auth: str = Column(Text, nullable=False)
    creation_date: datetime = Column(TIMESTAMP(timezone=True), nullable=False)
    validation_date: Optional[datetime] = Column(TIMESTAMP(timezone=True), nullable=True)
    is_active: bool = Column(Boolean, nullable=False)



# This class is ised by Pydantic, which validated the data recieved from the request
class CreateUserRequest(BaseModel):

    email: str
    passwd_auth: str

    class Config:
        from_attributes = True
