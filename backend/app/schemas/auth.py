import re
from datetime import datetime

from pydantic import BaseModel, ConfigDict, EmailStr, Field, field_validator

PHONE_RE = re.compile(r"^[0-9+\-\s]{10,15}$")


def check_phone(v: str) -> str:
    if not PHONE_RE.match(v):
        raise ValueError("Enter a valid phone number")
    return v.strip()


class RegisterIn(BaseModel):
    model_config = ConfigDict(extra="forbid")
    name: str = Field(min_length=2, max_length=100)
    email: EmailStr
    phone: str
    password: str = Field(min_length=8, max_length=72)

    _phone = field_validator("phone")(check_phone)

    @field_validator("password")
    @classmethod
    def strong_enough(cls, v: str) -> str:
        if not (re.search(r"[A-Za-z]", v) and re.search(r"\d", v)):
            raise ValueError("Password must contain letters and numbers")
        return v


class LoginIn(BaseModel):
    email: EmailStr
    password: str = Field(min_length=1, max_length=72)


class UserOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    id: int
    name: str
    email: EmailStr
    phone: str
    role: str
    created_at: datetime


class TokenOut(BaseModel):
    access_token: str
    token_type: str = "bearer"
    user: UserOut
