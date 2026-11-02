from database import engine, Base
from models import( User,BankAccount,UPIAccount,DOCUMENT,BENEFICIARY,BENEFICIARYUPIAccount,BENEFICIARYBANKAccount,APICLIENT,
PAYOUT,IDEMPOTENCYKEY)
from routes.admin.admin_model import Admin
from routes.organization.organization_model import Organization,OrganizationUser,OrganizationAPICredential,OrganizationWallet
from routes.remitter.remitter_models import Remitter,RemitterDocument
from routes.organization.beneficiary.beneficiary_models import Beneficiary,BeneficiaryAccount

Base.metadata.create_all(bind=engine)

print("Database tables created successfully!")
