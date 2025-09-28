import uuid

from sqlalchemy import Column, String, Boolean, DateTime, DECIMAL, Integer, func
from sqlalchemy.orm import relationship
from sqlalchemy.dialects.postgresql import UUID

from core.database import Base

class Service(Base):
    __tablename__ = "services"
    id = Column(UUID(as_uuid=True), default=uuid.uuid4, index=True, primary_key=True)
    title = Column(String(200), nullable=False, index = True)
    description = Column(String(750), nullable=False)
    price = Column(DECIMAL(precision=10, scale=2), nullable=False, index = True)
    duration_minutes = Column(Integer,nullable=False)
    is_active = Column (Boolean, default=True, index = True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())

    bookings = relationship("Booking", back_populates="service", cascade = "all, delete-orphan")

