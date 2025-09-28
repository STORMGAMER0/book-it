from typing import List, Optional
from uuid import UUID
from decimal import Decimal
from sqlalchemy.orm import Session
from sqlalchemy import or_
from models.service import Service
from schema.service import ServiceCreate, ServiceUpdate, ServiceQuery


class ServiceCRUD:
    @staticmethod
    def get_service_by_id(db:Session, id: UUID) -> Optional[Service]:
        return db.query(Service).filter(Service.id == id).first()

    @staticmethod
    def create_service(db: Session, service: ServiceCreate):
        service_data =  service.model_dump()

        new_service = Service(**service_data)
        try:
            db.add(new_service)
            db.commit()
            db.refresh(new_service)
            return new_service
        except Exception as e:
            db.rollback()
            raise ValueError(f"Failed to create service: {str(e)}")

    @staticmethod
    def search(db: Session, query_params: ServiceQuery, skip: int = 0, limit: int = 100):
        """Search and filter services based on query parameters"""
        query = db.query(Service)

        # Filter by active status
        if query_params.active is not None:
            query = query.filter(Service.is_active == query_params.active)

        # Search by title or description
        if query_params.q:
            search_term = f"%{query_params.q}%"
            query = query.filter(
                or_(
                    Service.title.ilike(search_term),
                    Service.description.ilike(search_term)
                )
            )

        if query_params.price_min is not None:
            query = query.filter(Service.price >= query_params.price_min)

        if query_params.price_max is not None:
            query = query.filter(Service.price <= query_params.price_max)

        return query.offset(skip).limit(limit).all()

    @staticmethod
    def update_service(db: Session, service_id: UUID, service_update: ServiceUpdate) -> Optional[Service]:

        db_service = ServiceCRUD.get_service_by_id(db, service_id)
        if not db_service:
            return None

        updated_data = service_update.model_dump(exclude_unset=True)
        try:
            for field, value in updated_data.items():
                setattr(db_service, field, value)

            db.commit()
            db.refresh(db_service)
            return db_service
        except Exception as e:
            db.rollback()
            raise ValueError(f"Failed to update service: {str(e)}")

    @staticmethod
    def remove(db: Session, service_id: UUID):
        service = db.query(Service).get(service_id)

        if not service:
            return None

        try:
            db.delete(service)
            db.commit()
            return service
        except Exception as e:
            db.rollback()
            raise ValueError(f"Failed to delete service: {str(e)}")