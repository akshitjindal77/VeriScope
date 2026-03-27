from datetime import datetime

from pydantic import BaseModel, ConfigDict


class SignupRequest(BaseModel):
    email: str
    username: str
    password: str


class LoginRequest(BaseModel):
    email: str          # accepts email or username
    password: str


class TokenResponse(BaseModel):
    access_token: str
    token_type: str = "bearer"


class UserResponse(BaseModel):
    id: str
    email: str
    username: str
    created_at: datetime
    email_verified: bool = False

    model_config = ConfigDict(from_attributes=True)
