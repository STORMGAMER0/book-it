from typing import List, Optional
from uuid import UUID
from sqlalchemy.orm import Session
from sqlalchemy.exc import IntegrityError

from models.review import Review
from models.booking import Booking, BookingStatus
from models.service import Service
from schema.review import ReviewCreate, ReviewUpdate


class ReviewCRUD:
    @staticmethod
    def get_review_by_id(db: Session, review_id: UUID) -> Optional[Review]:

        return db.query(Review).filter(Review.id == review_id).first()

    @staticmethod
    def get_review_by_booking_id(db: Session, booking_id: UUID) -> Optional[Review]:

        return db.query(Review).filter(Review.booking_id == booking_id).first()

    @staticmethod
    def get_service_reviews(db: Session, service_id: UUID, skip: int = 0, limit: int = 100) -> List[Review]:

        return db.query(Review).join(Booking).filter(
            Booking.service_id == service_id
        ).offset(skip).limit(limit).all()

    @staticmethod
    def create_review(db: Session, review_data: ReviewCreate, user_id: UUID) -> Review:


        booking = db.query(Booking).filter(Booking.id == review_data.booking_id).first()
        if not booking:
            raise ValueError("Booking not found")


        if booking.user_id != user_id:
            raise ValueError("You can only review your own bookings")


        if booking.status != BookingStatus.COMPLETED:
            raise ValueError("You can only review completed bookings")


        existing_review = ReviewCRUD.get_review_by_booking_id(db, review_data.booking_id)
        if existing_review:
            raise ValueError("Review already exists for this booking")


        new_review = Review(
            booking_id=review_data.booking_id,
            rating=review_data.rating,
            comment=review_data.comment
        )

        try:
            db.add(new_review)
            db.commit()
            db.refresh(new_review)
            return new_review
        except IntegrityError as e:
            db.rollback()
            if "unique constraint" in str(e).lower():
                raise ValueError("Review already exists for this booking")
            raise ValueError(f"Failed to create review: {str(e)}")
        except Exception as e:
            db.rollback()
            raise ValueError(f"Failed to create review: {str(e)}")

    @staticmethod
    def update_review(db: Session, review_id: UUID, review_update: ReviewUpdate, user_id: Optional[UUID] = None,
                      is_admin: bool = False) -> Optional[Review]:

        review = ReviewCRUD.get_review_by_id(db, review_id)
        if not review:
            raise ValueError("Review not found")


        if not is_admin:
            booking = db.query(Booking).filter(Booking.id == review.booking_id).first()
            if not booking or booking.user_id != user_id:
                raise ValueError("Not authorized to update this review")


        update_data = review_update.model_dump(exclude_unset=True)

        try:
            for field, value in update_data.items():
                setattr(review, field, value)

            db.commit()
            db.refresh(review)
            return review
        except Exception as e:
            db.rollback()
            raise ValueError(f"Failed to update review: {str(e)}")

    @staticmethod
    def delete_review(db: Session, review_id: UUID, user_id: Optional[UUID] = None, is_admin: bool = False) -> bool:

        review = ReviewCRUD.get_review_by_id(db, review_id)
        if not review:
            raise ValueError("Review not found")


        if not is_admin:
            booking = db.query(Booking).filter(Booking.id == review.booking_id).first()
            if not booking or booking.user_id != user_id:
                raise ValueError("Not authorized to delete this review")

        try:
            db.delete(review)
            db.commit()
            return True
        except Exception as e:
            db.rollback()
            raise ValueError(f"Failed to delete review: {str(e)}")

    @staticmethod
    def get_user_reviews(db: Session, user_id: UUID, skip: int = 0, limit: int = 100) -> List[Review]:

        return db.query(Review).join(Booking).filter(
            Booking.user_id == user_id
        ).offset(skip).limit(limit).all()

    @staticmethod
    def get_service_review_stats(db: Session, service_id: UUID) -> dict:

        reviews = ReviewCRUD.get_service_reviews(db, service_id)

        if not reviews:
            return {
                "total_reviews": 0,
                "average_rating": 0.0
            }

        total_reviews = len(reviews)
        total_rating = sum(review.rating for review in reviews)
        average_rating = round(total_rating / total_reviews, 2)

        return {
            "total_reviews": total_reviews,
            "average_rating": average_rating
        }