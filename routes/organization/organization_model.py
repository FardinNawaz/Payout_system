import uuid
from datetime import datetime
from sqlalchemy import String,Boolean,DateTime,ForeignKey,Numeric
from sqlalchemy.orm import Mapped,mapped_column
from database import Base
from decimal import Decimal

class Organization(Base):
    __tablename__="organizations"
    org_id:Mapped[str]=mapped_column(
        String(36),
        primary_key=True,
        default=lambda : str(uuid.uuid4())
    )
    org_name:Mapped[str]=mapped_column(
        String(150),
        nullable=False
    )
    email:Mapped[str]=mapped_column(
        String(255),
        unique=True,
        nullable=False
    )
    password_hash: Mapped[str] = mapped_column(
    String(255),
    nullable=False
    )
    phone: Mapped[str] = mapped_column(
        String(20),
        nullable=False
    )
    created_by_admin_id: Mapped[str] = mapped_column(
        ForeignKey("admins.admin_id"),
        nullable=False,
        index=True
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

class OrganizationWallet(Base):
    __tablename__ = "organization_wallets"
    wallet_id:Mapped[str]=mapped_column(
        String(36),
        primary_key=True,
        default=lambda:str(uuid.uuid4())
    )

    org_id:Mapped[str]=mapped_column(
        ForeignKey("organizations.org_id"),
        unique=True,
        nullable=False
    )
    balance: Mapped[Decimal] = mapped_column(
        Numeric(15, 2),
        default=Decimal("0.00"),
        nullable=False
    )
    currency: Mapped[str] = mapped_column(
        String(3),
        default="INR",
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


class OrganizationAPICredential(Base):
    __tablename__="organization_api_credentials"

    org_id: Mapped[str] = mapped_column(
        ForeignKey("organizations.org_id"),
        primary_key=True
    )

    api_key: Mapped[str] = mapped_column(
        String(255),
        unique=True,
        nullable=False
    )

    api_secret: Mapped[str] = mapped_column(
        String(512),
        nullable=False
    )

    webhook_url: Mapped[str | None] = mapped_column(
        String(500),
        nullable=True
    )

    webhook_secret_encrypted: Mapped[str | None] = mapped_column(
        String(512),
        nullable=True
    )


class OrganizationUser(Base):
    __tablename__ = "organization_users"

    user_id: Mapped[str] = mapped_column(
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
        unique=True,
        nullable=False
    )

    password_hash: Mapped[str] = mapped_column(
        String(255),
        nullable=False
    )

    role: Mapped[str] = mapped_column(
        String(50),
        default="ORG_USER",
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