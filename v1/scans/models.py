from v1.bd.database import base
from sqlalchemy import Column, Integer, TIMESTAMP, Text, Float, ForeignKey


class Scans(base):

    __tablename__ = "scans"

    id_scans = Column(Integer, primary_key=True, index=True)
    scan_started = Column(TIMESTAMP(timezone=True), nullable=True)
    scan_ended = Column(TIMESTAMP(timezone=True), nullable=True)
    file_name = Column(Text, nullable=False)
    file_bytes_size = Column(Float, nullable=False)
    user_id = Column(Integer, ForeignKey("pdf_atlas.users.id_users"), nullable=False)

    class Config:
        from_attributes = True
