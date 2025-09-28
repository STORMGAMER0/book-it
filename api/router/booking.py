from typing import List, Optional
from uuid import UUID
from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.orm import Session

from core.database import get_db
from core.security import get_current_user, require_admin
from crud.booking import BookingCRUD
from crud.user import UserCRUD
from models.user import User
from models.booking import BookingStatus
from schema.booking import BookingCreate, BookingUpdate, BookingQuery, BookingResponse

booking_router = APIRouter(tags=["bookings"], prefix="/bookings")


@booking_router.post("/", response_model=BookingResponse, status_code=status.HTTP_201_CREATED)
def create_booking(
        booking_in: BookingCreate,
        current_user: User = Depends(get_current_user),
        db: Session = Depends(get_db)
):

    try:
        booking = BookingCRUD.create_booking(db, booking_in, current_user.id)
        return booking
    except ValueError as e:
        if "conflicts with existing booking" in str(e):
            raise HTTPException(
                status_code=status.HTTP_409_CONFLICT,
                detail=str(e)
            )
        else:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=str(e)
            )


@booking_router.get("/", response_model=List[BookingResponse], status_code=status.HTTP_200_OK)
def get_bookings(
        status_filter: Optional[BookingStatus] = Query(None, alias="status", description="Filter by booking status"),
        from_date: Optional[str] = Query(None, alias="from", description="Filter bookings from this date (ISO format)"),
        to_date: Optional[str] = Query(None, alias="to", description="Filter bookings until this date (ISO format)"),
        skip: int = Query(0, ge=0),
        limit: int = Query(100, le=100),
        current_user: User = Depends(get_current_user),
        db: Session = Depends(get_db)
):

    parsed_from_date = None
    parsed_to_date = None

    try:
        if from_date:
            from datetime import datetime
            parsed_from_date = datetime.fromisoformat(from_date.replace('Z', '+00:00'))
        if to_date:
            parsed_to_date = datetime.fromisoformat(to_date.replace('Z', '+00:00'))
    except ValueError:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Invalid date format. Use ISO format (YYYY-MM-DDTHH:MM:SS)"
        )


    is_admin = UserCRUD.is_admin(current_user)

    if is_admin:

        query_params = BookingQuery(
            status=status_filter,
            from_date=parsed_from_date,
            to_date=parsed_to_date
        )
        bookings = BookingCRUD.get_all_bookings(db, query_params, skip, limit)
    else:

        bookings = BookingCRUD.get_user_bookings(db, current_user.id, skip, limit)


        if status_filter:
            bookings = [b for b in bookings if b.status == status_filter]
        if parsed_from_date:
            bookings = [b for b in bookings if b.start_time >= parsed_from_date]
        if parsed_to_date:
            bookings = [b for b in bookings if b.end_time <= parsed_to_date]

    return bookings


@booking_router.get("/{booking_id}", response_model=BookingResponse, status_code=status.HTTP_200_OK)
def get_booking_by_id(
        booking_id: UUID,
        current_user: User = Depends(get_current_user),
        db: Session = Depends(get_db)
):

    booking = BookingCRUD.get_booking_by_id(db, booking_id)

    if not booking:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Booking not found"
        )


    is_admin = UserCRUD.is_admin(current_user)
    if not is_admin and booking.user_id != current_user.id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not authorized to view this booking"
        )

    return booking


@booking_router.patch("/{booking_id}", response_model=BookingResponse, status_code=status.HTTP_200_OK)
def update_booking(
        booking_id: UUID,
        booking_update: BookingUpdate,
        current_user: User = Depends(get_current_user),
        db: Session = Depends(get_db)
):

    is_admin = UserCRUD.is_admin(current_user)

    try:
        updated_booking = BookingCRUD.update_booking(
            db,
            booking_id,
            booking_update,
            current_user.id if not is_admin else None,
            is_admin
        )
        return updated_booking
    except ValueError as e:
        if "not found" in str(e):
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=str(e)
            )
        elif "not authorized" in str(e).lower():
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail=str(e)
            )
        elif "conflicts with existing booking" in str(e):
            raise HTTPException(
                status_code=status.HTTP_409_CONFLICT,
                detail=str(e)
            )
        else:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=str(e)
            )


@booking_router.delete("/{booking_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_booking(
        booking_id: UUID,
        current_user: User = Depends(get_current_user),
        db: Session = Depends(get_db)
):

    is_admin = UserCRUD.is_admin(current_user)

    try:
        BookingCRUD.delete_booking(
            db,
            booking_id,
            current_user.id if not is_admin else None,
            is_admin
        )
        return None
    except ValueError as e:
        if "not found" in str(e):
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=str(e)
            )
        elif "not authorized" in str(e).lower():
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail=str(e)
            )
        else:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=str(e)
            )