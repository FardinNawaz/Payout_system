
import uuid
from datetime import datetime
from sqlalchemy import LargeBinary

from sqlalchemy import (
    String,
    Boolean,
    DateTime,
    ForeignKey
)
from sqlalchemy.orm import Mapped, mapped_column

from database import Base


class Remitter(Base):
    __tablename__ = "remitters"

    remitter_id: Mapped[str] = mapped_column(
        String(36),
        primary_key=True,
        default=lambda: str(uuid.uuid4())
    )

    org_id: Mapped[str] = mapped_column(
        ForeignKey("organizations.org_id"),
        nullable=False,
        index=True
    )

    name: Mapped[str] = mapped_column(
        String(150),
        nullable=False
    )

    email: Mapped[str] = mapped_column(
        String(255),
        nullable=False
    )

    phone: Mapped[str] = mapped_column(
        String(20),
        nullable=False
    )

    is_active: Mapped[bool] = mapped_column(
        Boolean,
        default=True,
        nullable=False
    )

    created_at: Mapped[datetime] = mapped_column(
        DateTime,
        default=datetime.utcnow,
        nullable=False
    )


class RemitterDocument(Base):
    __tablename__ = "remitter_documents"

    document_id: Mapped[str] = mapped_column(
        String(36),
        primary_key=True,
        default=lambda: str(uuid.uuid4())
    )

    remitter_id: Mapped[str] = mapped_column(
        ForeignKey("remitters.remitter_id"),
        nullable=False,
        index=True
    )

    document_type: Mapped[str] = mapped_column(
        String(50),
        nullable=False
    )

    document_number: Mapped[str | None] = mapped_column(
        String(100),
        nullable=True
    )

    document_data: Mapped[bytes] = mapped_column(
        LargeBinary,
        nullable=False
    )

    uploaded_at: Mapped[datetime] = mapped_column(
        DateTime,
        default=datetime.utcnow,
        nullable=False
    )
