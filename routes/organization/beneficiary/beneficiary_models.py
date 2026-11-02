
import uuid
from datetime import datetime

from sqlalchemy import (
    String,
    DateTime,
    ForeignKey,
    UniqueConstraint,
    CheckConstraint
)
from sqlalchemy.orm import Mapped, mapped_column

from database import Base


class Beneficiary(Base):
    __tablename__ = "beneficiaries"

    beneficiary_id: Mapped[str] = mapped_column(
        String(36),
        primary_key=True,
        default=lambda: str(uuid.uuid4())
    )

    remitter_id: Mapped[str] = mapped_column(
        ForeignKey("remitters.remitter_id"),
        nullable=False,
        index=True
    )

    name: Mapped[str] = mapped_column(
        String(150),
        nullable=False
    )

    email: Mapped[str | None] = mapped_column(
        String(255),
        nullable=True
    )

    phone: Mapped[str] = mapped_column(
        String(20),
        nullable=False
    )


    created_at: Mapped[datetime] = mapped_column(
        DateTime,
        default=datetime.utcnow,
        nullable=False
    )


class BeneficiaryAccount(Base):
    __tablename__ = "beneficiary_accounts"

    __table_args__ = (
        UniqueConstraint(
            "beneficiary_id",
            "account_number",
            name="uq_beneficiary_account_number"
        ),
        UniqueConstraint(
            "beneficiary_id",
            "upi_id",
            name="uq_beneficiary_upi_id"
        ),
        CheckConstraint(
            """
            (
                account_type = 'BANK'
                AND account_number IS NOT NULL
                AND ifsc_code IS NOT NULL
                AND upi_id IS NULL
            )
            OR
            (
                account_type = 'UPI'
                AND upi_id IS NOT NULL
                AND account_number IS NULL
                AND ifsc_code IS NULL
            )
            """,
            name="ck_beneficiary_account_type"
        )
    )

    account_id: Mapped[str] = mapped_column(
        String(36),
        primary_key=True,
        default=lambda: str(uuid.uuid4())
    )

    beneficiary_id: Mapped[str] = mapped_column(
        ForeignKey("beneficiaries.beneficiary_id"),
        nullable=False,
        index=True
    )

    account_type: Mapped[str] = mapped_column(
        String(20),
        nullable=False
    )

    account_number: Mapped[str | None] = mapped_column(
        String(255),
        nullable=True
    )

    ifsc_code: Mapped[str | None] = mapped_column(
        String(20),
        nullable=True
    )

    upi_id: Mapped[str | None] = mapped_column(
        String(255),
        nullable=True
    )

    created_at: Mapped[datetime] = mapped_column(
        DateTime,
        default=datetime.utcnow,
        nullable=False
    )
