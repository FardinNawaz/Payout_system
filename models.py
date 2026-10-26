import uuid
from sqlalchemy import String, ForeignKey, UniqueConstraint,Numeric
from sqlalchemy.orm import Mapped, mapped_column
from decimal import Decimal
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

class BENEFICIARY(Base):
    __tablename__="beneficiaries"

    beneficiary_id:Mapped[str]=mapped_column(
        String(36),
        primary_key=True,
        default=lambda :str(uuid.uuid4())
    )

    user_id:Mapped[str]=mapped_column(
        String(36),
        ForeignKey("users.user_id"),
        nullable=False,
        index=True
    )

    beneficiary_name:Mapped[str]=mapped_column(
        String(100),
        nullable=False
    )

class BENEFICIARYBANKAccount(Base):
    __tablename__="beneficiary_bank_account"

    __table_args__=(
        UniqueConstraint(
            "beneficiary_id",
            "account_number",
            name="uq_beneficairy_bank"
        ),
    )

    bank_id:Mapped[str]=mapped_column(
        String(50),
        primary_key=True,
        default=lambda :str(uuid.uuid4())
    )

    beneficiary_id:Mapped[str]=mapped_column(
        String(36),
        ForeignKey("beneficiaries.beneficiary_id"),
        nullable=False,
        index=True
    )

    bank_name:Mapped[str]=mapped_column(
        String(50),
        nullable=False
    )

    account_number:Mapped[str]=mapped_column(
        String(100),
        nullable=False
    )

    ifsc_code:Mapped[str]=mapped_column(
        String(50),
        nullable=False
    )

class BENEFICIARYUPIAccount(Base):
    __tablename__="beneficiary_upi_account"
    __table_args__=(
        UniqueConstraint(
            "beneficiary_id",
            "upi_id",
            name="uq_beneficiary_upi"
        ),
     )

    upi_account_id:Mapped[str]=mapped_column(
        String(36),
        primary_key=True,
        default=lambda :str(uuid.uuid4())
    )

    beneficiary_id:Mapped[str]=mapped_column(
        String(36),
        ForeignKey("beneficiaries.beneficiary_id"),
        nullable=False,
        index=True
    )

    upi_id:Mapped[str]=mapped_column(
        String(15),
        nullable=False
    )

class APICLIENT(Base):
    __tablename__="api_client"

    user_id:Mapped[str]=mapped_column(
        String(36),
        ForeignKey("users.user_id"),
        primary_key=True
    )
    api_key:Mapped[str]=mapped_column(
        String(100),
        unique=True,
        nullable=False,
        index=True
    )
    api_secret:Mapped[str]=mapped_column(
        String(255),
        nullable=False
    )

    webhook_url:Mapped[str]=mapped_column(
        String(500),
        nullable=False 
    )

    webhook_secret:Mapped[str]=mapped_column(
        String(255),
        nullable=False
    )

class PAYOUT(Base):
    __tablename__="payouts"

    payout_id:Mapped[str]=mapped_column(
        String(36),
        primary_key=True,
        default=lambda : str(uuid.uuid4()) 
    )

    user_id:Mapped[str]=mapped_column(
        String(36),
        ForeignKey("users.user_id"),
        index=True,
        nullable=False
    )
    sender_bank_id: Mapped[str | None] = mapped_column(
    String(36),
    ForeignKey("bank_account.bank_id"),
    nullable=True
    )
    sender_upi_account_id: Mapped[str | None] = mapped_column(
        String(36),
        ForeignKey("upi_account.upi_account_id"),
        nullable=True
    )
    beneficiary_id:Mapped[str]=mapped_column(
        String(36),
        ForeignKey("beneficiaries.beneficiary_id"),
        nullable=False,
        index=True
    )

    beneficiary_bank_id: Mapped[str | None] = mapped_column(
        String(50),
        ForeignKey("beneficiary_bank_account.bank_id"),
        nullable=True
    )

    beneficiary_upi_account_id: Mapped[str | None] = mapped_column(
        String(36),
        ForeignKey("beneficiary_upi_account.upi_account_id"),
        nullable=True
    )

    reference_id: Mapped[str] = mapped_column(
        String(100),
        nullable=False,
        unique=True,
        index=True
    )

    amount: Mapped[Decimal] = mapped_column(
    Numeric(12, 2),
    nullable=False
)

    currency: Mapped[str] = mapped_column(
        String(3),
        nullable=False,
        default="INR"
    )

    payment_mode: Mapped[str] = mapped_column(
        String(20),
        nullable=False
    )

    status: Mapped[str] = mapped_column(
        String(20),
        nullable=False,
        default="PENDING"
    )