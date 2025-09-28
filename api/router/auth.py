from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from core.database import get_db
from crud.user import UserCRUD
from schema.user import UserCreate, UserResponse, UserLogin
from core.security import create_access_token, create_refresh_token, verify_token,get_current_user
from schema.auth import LoginResponse, Token, RefreshTokenRequest
from models.user import User
auth_router = APIRouter(tags=["auth"], prefix="/auth")

@auth_router.post("/register", response_model=UserResponse, status_code=status.HTTP_201_CREATED)
def register_user(user:UserCreate, db:Session=Depends(get_db)):
    try:
        new_user = UserCRUD.create_user(db,user)
        return new_user
    except ValueError as e:
        if "email already registered" in str(e):
            raise HTTPException(
                status_code=status.HTTP_409_CONFLICT,
                detail="Email already registered"
            )
        else:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=str(e)
            )



@auth_router.post("/login", response_model=LoginResponse,status_code=status.HTTP_200_OK)
def login(login_data: UserLogin, db:Session = Depends(get_db)):

    user = UserCRUD.authenticate(db,login_data.email,login_data.password)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect email or password",
            headers={"WWW-Authenticate": "Bearer"},
        )

    access_token = create_access_token(data={"sub":str(user.id)})
    refresh_token = create_refresh_token(data = {"sub":str(user.id)})

    return LoginResponse(user=user, tokens=Token(access_token=access_token, refresh_token=refresh_token,token_type="bearer"))


@auth_router.post("/refresh", response_model=Token)
def refresh_token(refresh_request: RefreshTokenRequest, db : Session = Depends(get_db)):

    payload = verify_token(refresh_request.refresh_token,token_type="refresh")
    if payload is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid refresh token"
        )

    user_id = payload.get("sub")
    if user_id is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid refresh token"
        )


    user = UserCRUD.get_user_by_id(db, user_id)
    if user is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="User not found"
        )

    new_access_token = create_access_token(data={"sub": str(user.id)})
    return Token(access_token=new_access_token, refresh_token=refresh_request.refresh_token, token_type = "bearer")


@auth_router.post("/logout", status_code=status.HTTP_200_OK)
def logout(current_user: User = Depends(get_current_user)):
    return {
        "message": "Logout successful",
        "help": "i dont know how to implement a logout besides the access token expiring😭😭😭😭😭😭"
    }



