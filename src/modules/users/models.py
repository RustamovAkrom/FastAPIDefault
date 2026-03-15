from datetime import datetime
from enum import StrEnum

from sqlalchemy import (
    Boolean,
    DateTime,
    String,
    Text,
)
from sqlalchemy import (
    Enum as SQLEnum,
)
from sqlalchemy.orm import Mapped, mapped_column

from db.base import Base, IDMixin, TimestampMixin


class UserRole(StrEnum):
    SUPERADMIN = "superadmin"
    ADMIN = "admin"
    MODERATOR = "moderator"
    USER = "user"


class User(Base, IDMixin, TimestampMixin):
    __tablename__ = "users"

    # AUTH

    username: Mapped[str] = mapped_column(String(50), unique=True, index=True, nullable=False)

    email: Mapped[str] = mapped_column(String(255), unique=True, index=True, nullable=False)

    password: Mapped[str] = mapped_column(String(255), nullable=False)

    # PROFILE

    first_name: Mapped[str | None] = mapped_column(String(100))
    last_name: Mapped[str | None] = mapped_column(String(100))

    phone: Mapped[str | None] = mapped_column(String(30))

    avatar: Mapped[str | None] = mapped_column(String(255))

    bio: Mapped[str | None] = mapped_column(Text)

    # PERMISSIONS

    role: Mapped[UserRole] = mapped_column(SQLEnum(UserRole), default=UserRole.USER, nullable=False)

    is_active: Mapped[bool] = mapped_column(Boolean, default=True)

    is_staff: Mapped[bool] = mapped_column(Boolean, default=False)

    is_superuser: Mapped[bool] = mapped_column(Boolean, default=False)

    # SECURITY

    is_verified: Mapped[bool] = mapped_column(Boolean, default=False)

    last_login: Mapped[datetime | None] = mapped_column(DateTime)

    last_login_ip: Mapped[str | None] = mapped_column(String(45))

    login_attempts: Mapped[int] = mapped_column(default=0)

    def __str__(self) -> str:
        return f"{self.username} ({self.email})"
