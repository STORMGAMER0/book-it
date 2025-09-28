from datetime import datetime
from typing import Optional
from uuid import UUID
from pydantic import BaseModel, Field, field_validator
from models.booking import BookingStatus


class BookingBase(BaseModel):
    service_id: UUID
    start_time: datetime
    end_time: datetime

    @field_validator('end_time')
    @classmethod
    def end_time_must_be_after_start_time(cls, v, info):
        if hasattr(info, 'data') and 'start_time' in info.data and v <= info.data['start_time']:
            raise ValueError('end_time must be after start_time')
        return v


class BookingCreate(BookingBase):
    pass


class BookingUpdate(BaseModel):
    """Schema for updating a booking"""
    start_time: Optional[datetime] = None
    end_time: Optional[datetime] = None
    status: Optional[BookingStatus] = None

    @field_validator('end_time')
    @classmethod
    def end_time_must_be_after_start_time(cls, v, info):
        if hasattr(info, 'data') and 'start_time' in info.data and info.data['start_time'] and v and v <= info.data[
            'start_time']:
            raise ValueError('end_time must be after start_time')
        return v


class BookingResponse(BookingBase):
    id: UUID
    user_id: UUID
    status: BookingStatus
    created_at: datetime

    class Config:
        from_attributes = True


class BookingQuery(BaseModel):
    status: Optional[BookingStatus] = Field(None, description="Filter by booking status")
    from_date: Optional[datetime] = Field(None, description="Filter bookings from this date", alias="from")
    to_date: Optional[datetime] = Field(None, description="Filter bookings until this date", alias="to")

    @field_validator('to_date')
    @classmethod
    def to_date_must_be_after_from_date(cls, v, info):
        if hasattr(info, 'data') and 'from_date' in info.data and info.data['from_date'] and v and v <= info.data[
            'from_date']:
            raise ValueError('to_date must be after from_date')
        return v