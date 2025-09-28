from typing import List, Optional
from uuid import UUID
from datetime import datetime, timezone
from sqlalchemy.orm import Session
from sqlalchemy import and_, or_
from fastapi import HTTPException, status

from models.booking import Booking, BookingStatus
from models.service import Service
from schema.booking import BookingCreate, BookingUpdate, BookingQuery


class BookingCRUD:
    @staticmethod
    def get_booking_by_id(db: Session, booking_id: UUID) -> Optional[Booking]:
        """Get booking by ID"""
        return db.query(Booking).filter(Booking.id == booking_id).first()

    @staticmethod
    def get_user_bookings(db: Session, user_id: UUID, skip: int = 0, limit: int = 100) -> List[Booking]:
        """Get all bookings for a specific user"""
        return db.query(Booking).filter(Booking.user_id == user_id).offset(skip).limit(limit).all()

    @staticmethod
    def get_all_bookings(db: Session, query_params: BookingQuery, skip: int = 0, limit: int = 100) -> List[Booking]:

        query = db.query(Booking)


        if query_params.status:
            query = query.filter(Booking.status == query_params.status)


        if query_params.from_date:
            query = query.filter(Booking.start_time >= query_params.from_date)

        if query_params.to_date:
            query = query.filter(Booking.end_time <= query_params.to_date)

        return query.offset(skip).limit(limit).all()

    @staticmethod
    def check_booking_conflicts(db: Session, service_id: UUID, start_time: datetime, end_time: datetime,
                                exclude_booking_id: Optional[UUID] = None) -> bool:

        query = db.query(Booking).filter(
            and_(
                Booking.service_id == service_id,
                Booking.status.in_([BookingStatus.CONFIRMED, BookingStatus.PENDING]),
                or_(

                    and_(Booking.start_time <= start_time, Booking.end_time > start_time),

                    and_(Booking.start_time < end_time, Booking.end_time >= end_time),

                    and_(Booking.start_time >= start_time, Booking.end_time <= end_time)
                )
            )
        )


        if exclude_booking_id:
            query = query.filter(Booking.id != exclude_booking_id)

        return query.first() is not None

    @staticmethod
    def create_booking(db: Session, booking_data: BookingCreate, user_id: UUID) -> Booking:

        service = db.query(Service).filter(Service.id == booking_data.service_id).first()
        if not service:
            raise ValueError("Service not found")
        if not service.is_active:
            raise ValueError("Service is not active")

        # Check for conflicts
        if BookingCRUD.check_booking_conflicts(db, booking_data.service_id, booking_data.start_time,
                                               booking_data.end_time):
            raise ValueError("Booking conflicts with existing booking")


        if booking_data.start_time >= booking_data.end_time:
            raise ValueError("Start time must be before end time")


        if booking_data.start_time <= datetime.now(timezone.utc):
            raise ValueError("Cannot book in the past")


        new_booking = Booking(
            user_id=user_id,
            service_id=booking_data.service_id,
            start_time=booking_data.start_time,
            end_time=booking_data.end_time,
            status=BookingStatus.PENDING
        )

        try:
            db.add(new_booking)
            db.commit()
            db.refresh(new_booking)
            return new_booking
        except Exception as e:
            db.rollback()
            raise ValueError(f"Failed to create booking: {str(e)}")

    @staticmethod
    def update_booking(db: Session, booking_id: UUID, booking_update: BookingUpdate, user_id: Optional[UUID] = None,
                       is_admin: bool = False) -> Optional[Booking]:

        booking = BookingCRUD.get_booking_by_id(db, booking_id)
        if not booking:
            raise ValueError("Booking not found")

        # Check permissions
        if not is_admin and booking.user_id != user_id:
            raise ValueError("Not authorized to update this booking")

        update_data = booking_update.model_dump(exclude_unset=True)

        # If updating times, check for conflicts
        new_start_time = update_data.get('start_time', booking.start_time)
        new_end_time = update_data.get('end_time', booking.end_time)

        if 'start_time' in update_data or 'end_time' in update_data:
            # Users can only reschedule if booking is pending or confirmed
            if not is_admin and booking.status not in [BookingStatus.PENDING, BookingStatus.CONFIRMED]:
                raise ValueError("Cannot reschedule completed or cancelled booking")


            if BookingCRUD.check_booking_conflicts(db, booking.service_id, new_start_time, new_end_time, booking_id):
                raise ValueError("Updated booking conflicts with existing booking")


            if new_start_time <= datetime.now(timezone.utc):
                raise ValueError("Cannot reschedule to past time")


        if 'status' in update_data:
            new_status = update_data['status']
            if not is_admin:
                # Users can only cancel their own bookings
                if new_status == BookingStatus.CANCELLED and booking.status in [BookingStatus.PENDING,
                                                                                BookingStatus.CONFIRMED]:
                    pass  # Allow cancellation
                else:
                    raise ValueError("Users can only cancel pending or confirmed bookings")

        try:
            for field, value in update_data.items():
                setattr(booking, field, value)

            db.commit()
            db.refresh(booking)
            return booking
        except Exception as e:
            db.rollback()
            raise ValueError(f"Failed to update booking: {str(e)}")

    @staticmethod
    def delete_booking(db: Session, booking_id: UUID, user_id: Optional[UUID] = None, is_admin: bool = False) -> bool:

        booking = BookingCRUD.get_booking_by_id(db, booking_id)
        if not booking:
            raise ValueError("Booking not found")

        # Check permissions
        if not is_admin:
            if booking.user_id != user_id:
                raise ValueError("Not authorized to delete this booking")

            # Users can only delete before start time
            if booking.start_time <= datetime.now(timezone.utc):
                raise ValueError("Cannot delete booking after start time")

        try:
            db.delete(booking)
            db.commit()
            return True
        except Exception as e:
            db.rollback()
            raise ValueError(f"Failed to delete booking: {str(e)}")