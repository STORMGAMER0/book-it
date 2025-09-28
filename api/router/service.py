from typing import List, Optional
from uuid import UUID
from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.orm import Session

from core.database import get_db
from core.security import get_current_user, require_admin
from crud.service import ServiceCRUD
from models.user import User
from schema.service import ServiceCreate, ServiceUpdate, ServiceQuery, ServiceResponse

service_router = APIRouter(tags=["service"], prefix="/services")

@service_router.post("/",response_model=ServiceResponse, status_code=status.HTTP_201_CREATED)
def create_service(
    service_in: ServiceCreate,
    current_user: User = Depends(require_admin),
    db: Session = Depends(get_db)
):
    try:
        service = ServiceCRUD.create_service(db,service_in)
        return service
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )

@service_router.get("/", response_model=List[ServiceResponse], status_code=status.HTTP_200_OK)
def get_services(
        q: Optional[str] = Query(None, description="Search query"),
        price_min: Optional[float] = Query(None, description="Minimum price"),
        price_max: Optional[float] = Query(None, description="Maximum price"),
        active: Optional[bool] = Query(True, description="Filter by active status"),
        skip: int = Query(0, ge=0),
        limit: int = Query(100, le=100),
        db: Session = Depends(get_db)
):
    query_params = ServiceQuery(q=q, price_min=price_min, price_max=price_max, active=active)
    services = ServiceCRUD.search(db, query_params=query_params, skip=skip, limit=limit)

    return [
        {
            "id": str(service.id),
            "title": service.title,
            "description": service.description,
            "price": float(service.price),
            "duration_minutes": service.duration_minutes,
            "is_active": service.is_active,
            "created_at": str(service.created_at)
        }
        for service in services
    ]

@service_router.get("/{service_id}", response_model=ServiceResponse, status_code=status.HTTP_200_OK)
def get_service_by_id(service_id:UUID, db: Session= Depends(get_db)):
    service = ServiceCRUD.get_service_by_id(db, service_id)
    if not service:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Service not found"
        )
    return service


@service_router.patch("/{service_id}",response_model=ServiceResponse, status_code=status.HTTP_200_OK )
def update_service(
        service_id: UUID,
        service_update: ServiceUpdate,
        current_user: User = Depends(require_admin),
        db: Session = Depends(get_db)
):

    try:
        updated_service = ServiceCRUD.update_service(db, service_id,service_update)
        if not updated_service:  # Handle None case
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Service not found"
            )
        return updated_service
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )


@service_router.delete("/{service_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_service(
        service_id: UUID,
        current_user: User = Depends(require_admin),
        db: Session = Depends(get_db)
):

    ServiceCRUD.remove(db, service_id)
    return None
