from v1.bd.database import base
from sqlalchemy import Column, Integer, ForeignKey, TIMESTAMP, Enum
from enum import Enum as PyEnum

class mail_types_enum(PyEnum):
    validation='VALIDATION'

class Emails(base):

    __tablename__ = "emails"

    id_emails = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("pdf_atlas.users.id_users"), nullable=False)
    creation_date = Column(TIMESTAMP(timezone=True), nullable=False)
    mail_type = Column(
        Enum(mail_types_enum, name='mail_type', creation_type=False),
        nullable=False
    )

    class Config:
        from_attributes = True




