import os
import secrets
import bcrypt
from dotenv import load_dotenv
from fastapi import APIRouter,Header,HTTPException,Depends
from sqlalchemy.orm import Session
from sqlalchemy.exc import IntegrityError
from decimal import Decimal
from database import get_db
from cryptography.fernet import Fernet
from routes.organization.organization_model import Organization,OrganizationWallet,OrganizationAPICredential
from routes.organization.organization_schema import(
    OrganizationCreate,OrganizationResponse,
    OrganizationWalletResponse,OrganizationWalletCreate,
    OrganizationAPICredentialResponse,
    OrganizationWebhookConfig,OrganizationWebhookResponse,
    OrganizationWalletCredit,OrganizationWalletCreditResponse
)
from routes.admin.admin import check_admin
load_dotenv()

router=APIRouter(
    prefix="/api/v1/admin/organizations",
    tags=["Organization"]
)

@router.post("/",response_model=OrganizationResponse, status_code=201)
def create_organization(
    data: OrganizationCreate,
    access_token: str | None = Header(default=None),
    db: Session = Depends(get_db)
):
    if not access_token:
        raise HTTPException(
            status_code=401,
            detail="Access token is required"
        )
    current_admin=check_admin(access_token,db)
    email = str(data.email).lower()

    existing_organization = db.query(Organization).filter(
        Organization.email == email
    ).first()

    if existing_organization:
        raise HTTPException(
            status_code=409,
            detail="Organization email already exists"
        )
    password_hash = bcrypt.hashpw(
        data.password.encode("utf-8"),
        bcrypt.gensalt()
    ).decode("utf-8")
    new_organization = Organization(
        org_name=data.org_name,
        email=email,
        password_hash=password_hash,
        phone=data.phone,
        created_by_admin_id=current_admin.admin_id,
        is_active=True
    )
    try:
        db.add(new_organization)
        db.commit()
        db.refresh(new_organization)

        return new_organization
    except IntegrityError:
        db.rollback()
        raise HTTPException(
            status_code=409,
            detail="Organization email already exists"
        )
    except Exception:
        db.rollback()
        raise HTTPException(
            status_code=500,
            detail="Failed to create organization"
        )

@router.post(
    "/{org_id}/wallet",
    response_model=OrganizationWalletResponse,
    status_code=201
)
def create_organization_wallet(
    org_id: str,
    data: OrganizationWalletCreate,
    access_token: str | None = Header(default=None),
    db: Session = Depends(get_db)
):
    if not access_token:
        raise HTTPException(
            status_code=401,
            detail="Access token is required"
        )
    
    current_admin = check_admin(access_token, db)

    organization = db.query(Organization).filter(
        Organization.org_id == org_id
    ).first()

    if not organization:
        raise HTTPException(
            status_code=404,
            detail="Organization not found"
        )
    existing_wallet = db.query(OrganizationWallet).filter(
        OrganizationWallet.org_id == org_id
    ).first()

    if existing_wallet:
        raise HTTPException(
            status_code=409,
            detail="Wallet already exists for this organization"
        )

    new_wallet = OrganizationWallet(
        org_id=org_id,
        balance=Decimal("0.00"),
        currency=data.currency,
        is_active=True
    )

    try:
        db.add(new_wallet)
        db.commit()
        db.refresh(new_wallet)

        return new_wallet

    except IntegrityError:
        db.rollback()
        raise HTTPException(
            status_code=409,
            detail="Wallet already exists"
        )

    except Exception:
        db.rollback()
        raise HTTPException(
            status_code=500,
            detail="Failed to create organization wallet"
        )

@router.post(
    "/{org_id}/api-credentials",
    response_model=OrganizationAPICredentialResponse,
    status_code=201
)
def create_organization_api_credentials(
    org_id: str,
    access_token: str | None = Header(default=None),
    db: Session = Depends(get_db)
):
    if not access_token:
        raise HTTPException(
            status_code=401,
            detail="Access token is required"
        )
    organization = db.query(Organization).filter(
        Organization.org_id == org_id
    ).first()
    if not organization:
        raise HTTPException(
            status_code=404,
            detail="Organization not found"
        )
    existing_credentials = db.query(
        OrganizationAPICredential
    ).filter(
        OrganizationAPICredential.org_id == org_id
    ).first()
    if existing_credentials:
        raise HTTPException(
            status_code=409,
            detail="API credentials already exist for this organization"
        )
    encryption_key = os.getenv("API_SECRET_ENCRYPTION_KEY")

    if not encryption_key:
        raise HTTPException(
            status_code=500,
            detail="API encryption key is not configured"
        )
    try:
        cipher = Fernet(encryption_key.encode())
        api_key = secrets.token_urlsafe(32)
        api_secret = secrets.token_urlsafe(48)

        encrypted_secret = cipher.encrypt(
            api_secret.encode()
        ).decode()

        new_credentials = OrganizationAPICredential(
            org_id=org_id,
            api_key=api_key,
            api_secret=encrypted_secret
        )
        db.add(new_credentials)
        db.commit()

        return OrganizationAPICredentialResponse(
            id=org_id,
            api_key=api_key,
            api_secret=api_secret
        )

    except IntegrityError:
        db.rollback()
        raise HTTPException(
            status_code=409,
            detail="API credentials already exist"
        )

    except Exception:
        db.rollback()
        raise HTTPException(
            status_code=500,
            detail="Failed to generate API credentials"
        )

@router.put(
    "/{org_id}/webhook",
    response_model=OrganizationWebhookResponse,
    status_code=200
)
def configure_organization_webhook(
    org_id: str,
    data: OrganizationWebhookConfig,
    access_token: str | None = Header(default=None),
    db: Session = Depends(get_db)
):

    if not access_token:
        raise HTTPException(
            status_code=401,
            detail="Access token is required"
        )

    current_admin = check_admin(access_token, db)

    organization = db.query(Organization).filter(
        Organization.org_id == org_id
    ).first()

    if not organization:
        raise HTTPException(
            status_code=404,
            detail="Organization not found"
        )
    
    credentials = db.query(
        OrganizationAPICredential
    ).filter(
        OrganizationAPICredential.org_id == org_id
    ).first()

    if not credentials:
        raise HTTPException(
            status_code=404,
            detail="Organization API credentials not found. Generate API credentials first."
        )

    encryption_key = os.getenv("API_SECRET_ENCRYPTION_KEY")

    if not encryption_key:
        raise HTTPException(
            status_code=500,
            detail="API encryption key is not configured"
        )

    try:
        cipher = Fernet(encryption_key.encode())

        webhook_secret = secrets.token_urlsafe(48)

        encrypted_webhook_secret = cipher.encrypt(
            webhook_secret.encode()
        ).decode()

        credentials.webhook_url = str(data.webhook_url)

        credentials.webhook_secret_encrypted = (
            encrypted_webhook_secret
        )

        db.commit()
        db.refresh(credentials)

        return OrganizationWebhookResponse(
            id=org_id,
            webhook_url=data.webhook_url,
            webhook_secret=webhook_secret
        )

    except Exception:
        db.rollback()
        raise HTTPException(
            status_code=500,
            detail="Failed to configure organization webhook"
        )

@router.post(
    "/{org_id}/wallet/credit",
    response_model=OrganizationWalletCreditResponse,
    status_code=200
)
def credit_organization_wallet(
    org_id: str,
    data: OrganizationWalletCredit,
    access_token: str | None = Header(default=None),
    db: Session = Depends(get_db)
):
    if not access_token:
        raise HTTPException(
            status_code=401,
            detail="Access token is required"
        )

    current_admin = check_admin(access_token, db)

    organization = db.query(Organization).filter(
        Organization.org_id == org_id
    ).first()

    if not organization:
        raise HTTPException(
            status_code=404,
            detail="Organization not found"
        )

    wallet = db.query(OrganizationWallet).filter(
        OrganizationWallet.org_id == org_id
    ).with_for_update().first()

    if not wallet:
        raise HTTPException(
            status_code=404,
            detail="Organization wallet not found"
        )

    if not wallet.is_active:
        raise HTTPException(
            status_code=400,
            detail="Organization wallet is inactive"
        )

    previous_balance = wallet.balance
    credited_amount = data.amount

    try:
        wallet.balance = previous_balance+credited_amount

        db.commit()
        db.refresh(wallet)

        return OrganizationWalletCreditResponse(
            id=org_id,
            previous_balance=previous_balance,
            credited_amount=credited_amount,
            current_balance=wallet.balance,
            description=data.description
        )

    except Exception as e:
        db.rollback()

        import traceback
        traceback.print_exc()

        raise HTTPException(
            status_code=500,
            detail=f"Failed to credit organization wallet: {str(e)}"
        )