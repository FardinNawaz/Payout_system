from database import engine, Base
from models import( User,BankAccount,UPIAccount,DOCUMENT,BENEFICIARY,BENEFICIARYUPIAccount,BENEFICIARYBANKAccount,APICLIENT,
PAYOUT)

Base.metadata.create_all(bind=engine)

print("Database tables created successfully!")
