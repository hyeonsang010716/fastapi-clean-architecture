from sqlalchemy import Column, String, DateTime
from sqlalchemy.sql import func
from app.database.session import Base


class User(Base):
    __tablename__ = "user"
    
    email = Column(String(255), index=True, primary_key=True)
    name = Column(String(255), nullable=False)
    created_at = Column(DateTime(timezone=True), server_default=func.now())