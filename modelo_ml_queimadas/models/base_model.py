from datetime import datetime

from sqlalchemy import func
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column


class Base(DeclarativeBase):
    pass


class BaseModel(Base):
    __abstract__ = True

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    created_at: Mapped[datetime] = mapped_column(
        unique=False, server_default=func.now()
    )
    updated_at: Mapped[datetime] = mapped_column(
        unique=False, nullable=True, onupdate=func.now()
    )
