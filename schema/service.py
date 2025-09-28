from datetime import datetime
from decimal import Decimal
from typing import Optional
from uuid import UUID
from pydantic import BaseModel, Field


class ServiceBase(BaseModel):
    title: str = Field(..., min_length=1, max_length=200)
    description: str = Field(..., min_length=1, max_length=1000)
    price: Decimal = Field(..., gt=0, decimal_places=2)
    duration_minutes: int = Field(..., gt=0, le=480)  # Max 8 hours


class ServiceCreate(ServiceBase):
    is_active: Optional[bool] = True


class ServiceUpdate(BaseModel):
    title: Optional[str] = Field(None, min_length=1, max_length=200)
    description: Optional[str] = Field(None, min_length=1, max_length=1000)
    price: Optional[Decimal] = Field(None, gt=0, decimal_places=2)
    duration_minutes: Optional[int] = Field(None, gt=0, le=480)
    is_active: Optional[bool] = None


class ServiceResponse(ServiceBase):
    id: UUID
    is_active: bool
    created_at: datetime

    class Config:
        from_attributes = True


class ServiceQuery(BaseModel):
    q: Optional[str] = Field(None, description="Search query for title/description")
    price_min: Optional[Decimal] = Field(None, ge=0, description="Minimum price filter")
    price_max: Optional[Decimal] = Field(None, ge=0, description="Maximum price filter")
    active: Optional[bool] = Field(True, description="Filter by active status")