from typing import List
from uuid import UUID
from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.orm import Session

from core.database import get_db
from core.security import get_current_user, require_admin
from crud.review import ReviewCRUD
from crud.user import UserCRUD
from models.user import User
from schema.review import ReviewCreate, ReviewUpdate, ReviewResponse

review_router = APIRouter(tags=["reviews"], prefix="/reviews")


@review_router.post("/", response_model=ReviewResponse, status_code=status.HTTP_201_CREATED)
def create_review(
        review_in: ReviewCreate,
        current_user: User = Depends(get_current_user),
        db: Session = Depends(get_db)
):

    try:
        review = ReviewCRUD.create_review(db, review_in, current_user.id)
        return review
    except ValueError as e:
        if "not found" in str(e).lower():
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=str(e)
            )
        elif "already exists" in str(e):
            raise HTTPException(
                status_code=status.HTTP_409_CONFLICT,
                detail=str(e)
            )
        elif "not authorized" in str(e).lower() or "only review your own" in str(e):
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail=str(e)
            )
        else:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=str(e)
            )


@review_router.get("/{review_id}", response_model=ReviewResponse, status_code=status.HTTP_200_OK)
def get_review_by_id(
        review_id: UUID,
        db: Session = Depends(get_db)
):

    review = ReviewCRUD.get_review_by_id(db, review_id)

    if not review:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Review not found"
        )

    return review


@review_router.patch("/{review_id}", response_model=ReviewResponse, status_code=status.HTTP_200_OK)
def update_review(
        review_id: UUID,
        review_update: ReviewUpdate,
        current_user: User = Depends(get_current_user),
        db: Session = Depends(get_db)
):

    is_admin = UserCRUD.is_admin(current_user)

    try:
        updated_review = ReviewCRUD.update_review(
            db,
            review_id,
            review_update,
            current_user.id if not is_admin else None,
            is_admin
        )
        return updated_review
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


@review_router.delete("/{review_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_review(
        review_id: UUID,
        current_user: User = Depends(get_current_user),
        db: Session = Depends(get_db)
):

    is_admin = UserCRUD.is_admin(current_user)

    try:
        ReviewCRUD.delete_review(
            db,
            review_id,
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



@review_router.get("/services/{service_id}/reviews", response_model=List[ReviewResponse],
                   status_code=status.HTTP_200_OK)
def get_service_reviews(
        service_id: UUID,
        skip: int = Query(0, ge=0),
        limit: int = Query(100, le=100),
        db: Session = Depends(get_db)
):

    reviews = ReviewCRUD.get_service_reviews(db, service_id, skip, limit)
    return reviews


@review_router.get("/services/{service_id}/stats", status_code=status.HTTP_200_OK)
def get_service_review_stats(
        service_id: UUID,
        db: Session = Depends(get_db)
):

    stats = ReviewCRUD.get_service_review_stats(db, service_id)
    return stats