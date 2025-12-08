"""
Base model with audit fields and soft-delete functionality.

This module provides a base model (DBBaseModel) that all database models should inherit from.
It includes automatic tracking of creation, updates, and soft deletes.
"""

import uuid
from datetime import datetime
from typing import Optional

from sqlalchemy import Boolean, DateTime, String
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.inspection import inspect
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column


class Base(DeclarativeBase):
    """Base class for all SQLAlchemy models."""
    pass


class BaseModel(Base):
    """
    Base model with audit fields and soft-delete functionality.
    
    All models should inherit from this class to get automatic audit fields:
    - id: Primary key (UUID)
    - created_at: When the record was created
    - created_by: Who created the record (user UUID or identifier)
    - updated_at: When the record was last updated
    - updated_by: Who last updated the record
    - deleted_at: When the record was soft-deleted (NULL if not deleted)
    - deleted_by: Who deleted the record
    - is_deleted: Boolean flag for soft-delete (for easier querying)
    
    Soft-delete pattern:
    - Records are never physically deleted from the database
    - Instead, deleted_at is set to the current timestamp
    - deleted_by is set to the user who performed the deletion
    - is_deleted is set to True
    - Queries should filter out deleted records by default (WHERE is_deleted = False)
    
    Usage:
        class DBUser(DBBaseModel):
            __tablename__ = "usuarios"
            
            email: Mapped[str] = mapped_column(String(255), unique=True)
            nome: Mapped[str] = mapped_column(String(255))
            # ... other fields
    """
    
    __abstract__ = True  # This ensures SQLAlchemy doesn't create a table for this class
    
    # Primary key
    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        primary_key=True,
        default=uuid.uuid4,
        index=True,
        doc="Unique identifier for the record"
    )
    
    # Creation audit fields
    created_at: Mapped[datetime] = mapped_column(
        DateTime,
        default=datetime.utcnow,
        nullable=False,
        doc="Timestamp when the record was created"
    )
    
    created_by: Mapped[Optional[str]] = mapped_column(
        String(255),
        nullable=True,
        doc="Identifier of the user who created the record"
    )
    
    # Update audit fields
    updated_at: Mapped[datetime] = mapped_column(
        DateTime,
        default=datetime.utcnow,
        onupdate=datetime.utcnow,
        nullable=False,
        doc="Timestamp when the record was last updated"
    )
    
    updated_by: Mapped[Optional[str]] = mapped_column(
        String(255),
        nullable=True,
        doc="Identifier of the user who last updated the record"
    )
    
    # Soft-delete audit fields
    deleted_at: Mapped[Optional[datetime]] = mapped_column(
        DateTime,
        nullable=True,
        doc="Timestamp when the record was soft-deleted (NULL if not deleted)"
    )
    
    deleted_by: Mapped[Optional[str]] = mapped_column(
        String(255),
        nullable=True,
        doc="Identifier of the user who deleted the record"
    )
    
    is_deleted: Mapped[bool] = mapped_column(
        Boolean,
        default=False,
        nullable=False,
        index=True,
        doc="Boolean flag indicating if the record is deleted (for easier querying)"
    )
    
    def soft_delete(self, deleted_by: Optional[str] = None) -> None:
        """
        Perform a soft delete on this record.
        
        Args:
            deleted_by: Identifier of the user performing the deletion
        """
        self.deleted_at = datetime.utcnow()
        self.deleted_by = deleted_by
        self.is_deleted = True
    
    def restore(self) -> None:
        """
        Restore a soft-deleted record.
        """
        self.deleted_at = None
        self.deleted_by = None
        self.is_deleted = False
        
    def tables_json_data(self) -> dict:
        """
        Retorna um dicionário com os nomes das colunas e seus valores atuais do modelo.
        Útil para serialização e exportação de dados.
        """
        return {
            column.key: getattr(self, column.key)
            for column in inspect(self).mapper.column_attrs
        }
    
    def __repr__(self):
        return f"<{self.__class__.__name__}(id={self.id})>"
