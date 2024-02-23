from datetime import datetime
from pydantic import BaseModel


class UserBase(BaseModel):
    name: str

class GuestBase(BaseModel):
    name: str
    message: str

class MinecraftStatsBase(BaseModel):
    username: str
    stats: dict

class StatusBase(BaseModel):
    status: str

class StatusCreate(StatusBase):
    pass

class StatusPublic(StatusBase):
    id: int
    dt: datetime

    class Config:
        from_attributes = True

class MinecraftStats(MinecraftStatsBase):
    id: int

    class Config:
        from_attributes = True

class GuestCreate(GuestBase):
    pass

class GuestPrivate(GuestBase):
    id: int
    dt: datetime
    ip: str
    is_banned: bool

    class Config:
        from_attributes = True

class GuestPublic(GuestBase):
    id: int
    user: UserBase
    dt: datetime

    class Config:
        from_attributes = True

class UserPublic(UserBase):
    statuses: list[StatusPublic]
    guests: list[GuestPublic]

    class Config:
        from_attributes = True

class UserCreate(UserBase):
    pass

class UserPrivate(UserBase):
    api_key: str
    statuses: list[StatusPublic]
    guests: list[GuestPrivate]
    url: str

    class Config:
        from_attributes = True

class UserAdmin(UserPrivate):
    id: int

class ClientSession(BaseModel):
    user: UserPublic
    ip: str
    state: str
    cookie: str