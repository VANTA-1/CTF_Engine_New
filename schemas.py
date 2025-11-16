# schemas.py
from pydantic import BaseModel

class ChallengeBase(BaseModel):
    name: str
    description: str
    flag: str
    points: int

class Challenge(ChallengeBase):
    id: int

    class Config:
        from_attributes = True

class UserBase(BaseModel):
    username: str

class User(UserBase):
    id: int
    is_active: bool

    class Config:
        from_attributes = True