import uuid
from datetime import datetime
from decimal import Decimal

from sqlalchemy import (
    String,
    ForeignKey,
    Numeric,
    DateTime,
)
from sqlalchemy.orm import Mapped, mapped_column

from database import Base


class Payout(Base):
    __tablename__ = "payouts"

    payout_id: Mapped[str] = mapped_column(
        String(36),
        primary_key=True,
        default=lambda: str(uuid.uuid4())
    )

    org_id: Mapped[str] = mapped_column(
        ForeignKey("organizations.org_id"),
        nullable=False,
        index=True
    )

    wallet_id: Mapped[str] = mapped_column(
        ForeignKey("organization_wallets.wallet_id"),
        nullable=False
    )

    remitter_id: Mapped[str] = mapped_column(
        ForeignKey("remitters.remitter_id"),
        nullable=False
    )

    beneficiary_id: Mapped[str] = mapped_column(
        ForeignKey("beneficiaries.beneficiary_id"),
        nullable=False
    )

    account_id: Mapped[str] = mapped_column(
        ForeignKey("beneficiary_accounts.account_id"),
        nullable=False
    )

    amount: Mapped[Decimal] = mapped_column(
        Numeric(15, 2),
        nullable=False
    )

    currency: Mapped[str] = mapped_column(
        String(3),
        default="INR",
        nullable=False
    )

    payment_mode: Mapped[str] = mapped_column(
        String(10),
        nullable=False
    )

    status: Mapped[str] = mapped_column(
        String(20),
        default="PENDING",
        nullable=False
    )

    created_at: Mapped[datetime] = mapped_column(
        DateTime,
        default=datetime.utcnow,
        nullable=False
    )