from datetime import datetime

from sqlalchemy import String, JSON, DateTime, Boolean, ForeignKey
from sqlalchemy.orm import Mapped
from sqlalchemy.orm import mapped_column, relationship

from .database import Base



class Guest(Base):
    __tablename__ = "guest"

    id: Mapped[int] = mapped_column(primary_key=True)
    user_id: Mapped[int] = mapped_column(ForeignKey("user.id"))
    user: Mapped["User"] = relationship(back_populates="guests")
    dt: Mapped[datetime] = mapped_column(DateTime())
    name: Mapped[str] = mapped_column(String(40))
    message: Mapped[str] = mapped_column(String(128))
    ip: Mapped[str] = mapped_column(String(16))
    is_banned: Mapped[bool] = mapped_column(Boolean(), default=False)

class MinecraftStats(Base):
    __tablename__ = "mcstats"
    id: Mapped[int] = mapped_column(primary_key=True)
    username: Mapped[str] = mapped_column(String(16))
    stats: Mapped[dict] = mapped_column(JSON())

class Status(Base):
    __tablename__ = "status"

    id: Mapped[int] = mapped_column(primary_key=True)
    user_id: Mapped[int] = mapped_column(ForeignKey("user.id"))
    user: Mapped["User"] = relationship(back_populates="statuses")
    dt: Mapped[datetime] = mapped_column(DateTime())
    status: Mapped[str] = mapped_column(String(128))

class User(Base):
    __tablename__ = "user"

    id: Mapped[int] = mapped_column(primary_key=True)
    name: Mapped[str] = mapped_column(String(16), unique=True)
    api_key: Mapped[str] = mapped_column(String(32), unique=True)
    is_admin: Mapped[bool] = mapped_column(Boolean(), default=False)
    statuses: Mapped[list[Status]] = relationship(back_populates="user", cascade="all, delete-orphan")
    guests: Mapped[list[Guest]] = relationship(back_populates="user", cascade="all, delete-orphan")