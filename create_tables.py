from database import engine, Base
from models import User,BankAccount,UPIAccount,DOCUMENT

Base.metadata.create_all(bind=engine)

print("Database tables created successfully!")
