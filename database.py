
import os
from dotenv import load_dotenv
from sqlalchemy import create_engine
from sqlalchemy.orm import declarative_base,sessionmaker

load_dotenv()

DATABASE_URL = os.getenv("DATABASE_URL")

if not DATABASE_URL:
    raise ValueError("DATABASE_URL not found in .env")

engine = create_engine(DATABASE_URL)

Base=declarative_base()
sessionLocal=sessionmaker(
    bind=engine,
    autoflush=False,
    autocommit=False
)

def get_db():
    db=sessionLocal()
    try:
        yield db
    finally:
        db.close()