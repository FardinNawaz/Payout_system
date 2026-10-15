import uuid
from sqlalchemy import String, ForeignKey, UniqueConstraint
from sqlalchemy.orm import Mapped, mapped_column

from database import Base


class User(Base):
    __tablename__ = "users"

    user_id: Mapped[str] = mapped_column(
        String(36),
        primary_key=True,
        default=lambda: str(uuid.uuid4())
    )

    name: Mapped[str] = mapped_column(
        String(100),
        nullable=False
    )

    email: Mapped[str] = mapped_column(
        String(255),
        index=True,
        unique=True,
        nullable=False
    )

    password_hash: Mapped[str] = mapped_column(
        String(100),
        nullable=False
    )

    role: Mapped[str] = mapped_column(
        String(20),
        default="USER",
        nullable=False
    )


class BankAccount(Base):
    __tablename__ = "bank_account"

    __table_args__ = (
        UniqueConstraint(
            "user_id",
            "account_number",
            name="uq_user_bank_account"
        ),
    )

    bank_id: Mapped[str] = mapped_column(
        String(36),
        primary_key=True,
        default=lambda: str(uuid.uuid4())
    )

    user_id: Mapped[str] = mapped_column(
        String(36),
        ForeignKey("users.user_id"),
        nullable=False,
        index=True
    )

    bank_name: Mapped[str] = mapped_column(
        String(100),
        nullable=False
    )

    account_number: Mapped[str] = mapped_column(
        String(30),
        nullable=False
    )

    ifsc: Mapped[str] = mapped_column(
        String(15),
        nullable=False
    )


class UPIAccount(Base):
    __tablename__ = "upi_account"

    __table_args__ = (
        UniqueConstraint(
            "user_id",
            "upi_id",
            name="uq_user_upi_id"
        ),
    )

    upi_account_id: Mapped[str] = mapped_column(
        String(36),
        primary_key=True,
        default=lambda: str(uuid.uuid4())
    )

    user_id: Mapped[str] = mapped_column(
        String(36),
        ForeignKey("users.user_id"),
        nullable=False,
        index=True
    )

    upi_id: Mapped[str] = mapped_column(
        String(100),
        nullable=False
    )


class DOCUMENT(Base):
    __tablename__="Document"

    __table_args__=(
        UniqueConstraint(
            "user_id",
            "document_name",
            "document_number",
            name="uq_docum_id"
        ),
    )
    document_id:Mapped[str]=mapped_column(
        String(36),
        primary_key=True,
        default=lambda:str(uuid.uuid4())
    )

    user_id:Mapped[str]=mapped_column(
        String(36),
        ForeignKey("users.user_id"),
        nullable=False,
        index=True
    )
    document_name:Mapped[str]=mapped_column(
        String(30),
        nullable=False

    )

    document_number:Mapped[str]=mapped_column(
        String(50),
        nullable=False
    )

    document_pic_url:Mapped[str]=mapped_column(
        String(500),
        nullable=False
    )
