from enum import StrEnum

from sqlalchemy import Boolean, String, Enum as SQLEnum
from sqlalchemy.orm import Mapped, mapped_column

from db.base import Base


class UserRole(StrEnum):
    SUPERADMIN = "superadmin"
    ADMIN = "admin"
    MODERATOR = "moderator"
    USER = "user"


class User(Base):
    __tablename__ = "users"

    id: Mapped[int] = mapped_column(primary_key=True)
    username: Mapped[str] = mapped_column(String(50), unique=True, index=True)
    email: Mapped[str] = mapped_column(String(255), unique=True, index=True)
    password: Mapped[str] = mapped_column(String(255))

    role: Mapped[str] = mapped_column(
        SQLEnum(UserRole), 
        default=UserRole.USER, 
        nullable=False
    )
    is_active: Mapped[bool] = mapped_column(Boolean, default=True)
