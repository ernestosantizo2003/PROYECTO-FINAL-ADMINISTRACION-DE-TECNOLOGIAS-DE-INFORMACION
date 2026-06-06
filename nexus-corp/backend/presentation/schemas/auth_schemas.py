from pydantic import BaseModel


class LoginRequest(BaseModel):
    username: str
    password: str

    model_config = {"json_schema_extra": {"example": {"username": "admin", "password": "admin123"}}}


class UserInfoResponse(BaseModel):
    id: str
    username: str
    email: str
    full_name: str
    role: str
    role_id: str


class LoginResponse(BaseModel):
    access_token: str
    token_type: str
    user: UserInfoResponse


class TokenData(BaseModel):
    user_id: str
    username: str
    role: str
