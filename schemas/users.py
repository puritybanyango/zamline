# Owner: Helen Mezgebe
# Feature: User Registration and Secure Access

from uuid import UUID

from pydantic import BaseModel, ConfigDict, EmailStr, Field, field_validator

from models.companies import CompanyType
from models.users import UserRole


class RegisterRequest(BaseModel):
    company_type: CompanyType
    business_name: str = Field(min_length=2, max_length=100)
    registration_number: str = Field(min_length=2, max_length=20)
    company_email: EmailStr
    phone_number: str = Field(min_length=5, max_length=15)
    first_name: str = Field(min_length=1, max_length=50)
    last_name: str = Field(min_length=1, max_length=50)
    email: EmailStr
    password: str = Field(min_length=8, max_length=128)
    role: UserRole

    @field_validator("registration_number")
    @classmethod
    def normalize_registration_number(cls, value: str) -> str:
        return value.strip().upper()


class UserResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    user_id: UUID
    company_id: UUID
    first_name: str
    last_name: str
    email: EmailStr
    role: UserRole
    is_active: bool


class RegisterResponse(BaseModel):
    user: UserResponse
    message: str


class OtpVerifyRequest(BaseModel):
    email: EmailStr
    code: str = Field(min_length=6, max_length=6)


class EmailRequest(BaseModel):
    email: EmailStr


class LoginRequest(BaseModel):
    email: EmailStr
    password: str


class TokenResponse(BaseModel):
    access_token: str
    token_type: str = "bearer"
