from pydantic import BaseModel, ConfigDict
from schema.user import UserResponse


class Token(BaseModel):
    access_token: str
    refresh_token: str
    token_type: str = "bearer"


class TokenData(BaseModel):

    user_id: str
    email: str


class LoginResponse(BaseModel):
    user: UserResponse
    tokens: Token
    model_config = ConfigDict(from_attributes=True)


class RefreshTokenRequest(BaseModel):
    refresh_token: str