from datetime import datetime
from typing import Optional

from fastapi_users import schemas
from pydantic import BaseModel


class UserRead(schemas.BaseUser[int]):
    pass

    class Config:
        from_attributes = True

class UserCreate(schemas.BaseUserCreate):
    pass

class UserCreateRefs(schemas.BaseUserCreate):
    referral_code: Optional[str] = None
    pass

class ReferralRegistrationResponse(BaseModel):
    message: str
    user_id: int
class ReferralCodeResponse(BaseModel):
    code: str
    expires_in: int

class ReferralResponse(BaseModel):
    id: int  # ID записи реферала
    email: str  # Email реферала
    registration_date: datetime  # Дата регистрации реферала

class ReferralsById(BaseModel):
    id: int

class ReferralCodeByEmail(BaseModel):
    email: str