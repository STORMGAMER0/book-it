from datetime import datetime
from typing import Optional
from uuid import UUID
from pydantic import BaseModel, Field


class ReviewBase(BaseModel):
    rating: int = Field(..., ge=1, le=5, description="Rating from 1 to 5")
    comment: str = Field(..., min_length=1, max_length=1000)


class ReviewCreate(ReviewBase):
    booking_id: UUID


class ReviewUpdate(BaseModel):
    rating: Optional[int] = Field(None, ge=1, le=5, description="Rating from 1 to 5")
    comment: Optional[str] = Field(None, min_length=1, max_length=1000)


class ReviewResponse(ReviewBase):
    id: UUID
    booking_id: UUID
    created_at: datetime

    class Config:
        from_attributes = True