from uuid import UUID
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from core.database import get_db
from crud.user import UserCRUD
from models import User
from schema.user import UserUpdate, UserResponse
from core.security import hash_password, get_current_user

user_router = APIRouter(tags=["user"], prefix="/users")


@user_router.get("/me")
def get_current_user_profile(current_user: User = Depends(get_current_user)):


    # Debug
    print(f"Authenticated user: {current_user}")
    print(f"User type: {type(current_user)}")


    return {
        "id": str(current_user.id),
        "name": current_user.name,
        "email": current_user.email,
        "role": str(current_user.role),
        "created_at": str(current_user.created_at)
    }

@user_router.get("/{user_id}", response_model = UserResponse,status_code= status.HTTP_200_OK)
def get_user_by_id(user_id: UUID, db: Session = Depends(get_db)):
    user = UserCRUD.get_user_by_id(db,user_id)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found")
    return user

@user_router.get("/email/{email}",  status_code= status.HTTP_200_OK)
def get_user_by_email(email: str,
    db: Session = Depends(get_db)):
    user = UserCRUD.get_user_by_email(db, email)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found"
        )
    return user

@user_router.patch("/me", response_model=UserResponse)

def update_user_profile(user_update: UserUpdate, db:Session = Depends(get_db), current_user: User= Depends(get_current_user)):
        try:
            updated_user = UserCRUD.update_user(db,user_id=current_user.id,update_user=user_update)
            return updated_user
        except ValueError as e:
            raise HTTPException(
                status_code= status.HTTP_400_BAD_REQUEST,
                detail= str(e)
            )