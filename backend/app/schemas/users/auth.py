from pydantic import BaseModel, ConfigDict, EmailStr, Field


class RegisterRequest(BaseModel):
    full_name: str = Field(
        min_length=2,
        max_length=150,
    )

    email: EmailStr

    phone: str = Field(
        default=None,
        max_length=20,
    )

    password: str = Field(
        min_length=8,
        max_length=72,
    )


class LoginRequest(BaseModel):
    email: EmailStr

    password: str = Field(
        min_length=1,
        max_length=72,
    )


class UserResponse(BaseModel):
    model_config = ConfigDict(
        from_attributes=True
    )

    id: int
    full_name: str
    email: EmailStr
    phone: str | None
    role: str
    department: str | None
    is_active: bool


class TokenResponse(BaseModel):
    access_token: str
    token_type: str