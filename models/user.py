import enum
import uuid

from pydantic import EmailStr
from sqlalchemy import String, Float, Boolean, Integer, Column, Enum,DateTime
from sqlalchemy.orm import relationship
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.sql import func
from core.database import Base

class Roles(str, enum.Enum):
    USER = "user"
    ADMIN = "admin"

class User(Base):
    __tablename__ = "users"
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4, index = True)
    name = Column(String(100), nullable=False)
    email = Column(String(250), nullable=False, unique=True)
    password_hash = Column(String, nullable=False)
    role =Column(Enum(Roles, name="user_roles"), nullable=False, default=Roles.USER)
    created_at = Column(DateTime(timezone=True), server_default=func.now())

    bookings = relationship("Booking", back_populates= "user", cascade= "all, delete-orphan")
