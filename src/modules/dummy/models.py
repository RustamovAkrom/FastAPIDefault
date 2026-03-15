from sqlalchemy.orm import Mapped, mapped_column
from sqlalchemy.sql.sqltypes import String

from db.base import Base


class Dummy(Base):
    """Model for demo purpose."""

    __tablename__ = "dummy_model"
    __table_args__ = {"extend_existing": True}
    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    name: Mapped[str] = mapped_column(String(length=200))
