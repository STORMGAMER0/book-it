from typing import Optional
from uuid import UUID
from sqlalchemy.orm import Session
from models.user import User
from schema.user import UserCreate, UserUpdate
from core.security import hash_password, verify_password


class UserCRUD:
    @staticmethod
    def get_user_by_id(db: Session, id: UUID) -> Optional[User]:
        return db.query(User).filter(User.id == id).first()

    @staticmethod
    def get_user_by_email(db: Session, email: str) -> Optional[User]:
        return db.query(User).filter(User.email == email).first()

    @staticmethod
    def create_user(db: Session, user: UserCreate) -> User:
        available_user = UserCRUD.get_user_by_email(db, user.email)
        if available_user:
            raise ValueError("email already registered")
        user_data = user.model_dump(exclude={"password"})
        new_user = User(**user_data, password_hash=hash_password(user.password))
        try:
            db.add(new_user)
            db.commit()
        except Exception as e:
            db.rollback()
            raise ValueError(f"Failed to create user: {str(e)}")
        db.refresh(new_user)
        return new_user

    @staticmethod
    def authenticate(db:Session, email: str, password: str)-> Optional[User]:
        user = UserCRUD.get_user_by_email(db, email)
        if not user:
            return None
        if not verify_password(password, user.password_hash):
            return None
        return user

    @staticmethod
    def is_active(user: User) -> bool:
        return True

    @staticmethod
    def is_admin(user: User):
        return user.role.value == "admin"

    @staticmethod
    def update_user(db:Session, user_id:UUID, update_user: UserUpdate)-> Optional[User]:
        user = UserCRUD.get_user_by_id(db, user_id)
        if not user:
            return None

        updated_data= update_user.model_dump(exclude_unset=True)
        for field, value in updated_data.items():
            setattr(user, field,value)
        db.add(user)
        try:
            db.commit()
            db.refresh(user)
            return user
        except Exception as e:
            db.rollback()
            raise ValueError(f"Failed to update user: {str(e)}")

