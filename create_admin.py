
import bcrypt
from getpass import getpass

from database import sessionLocal
from models import User

db = sessionLocal()

try:
    email = input("Enter admin email: ").strip().lower()
    password = getpass("Enter admin password: ")
    name = input("Enter admin name: ").strip()

    existing_user = (
        db.query(User)
        .filter(User.email == email)
        .first()
    )

    if existing_user:
        print("This email already exists.")
    else:
        hashed_password = bcrypt.hashpw(
            password.encode(),
            bcrypt.gensalt()
        ).decode()

        admin = User(
            name=name,
            email=email,
            password_hash=hashed_password,
            role="ADMIN"
        )

        db.add(admin)
        db.commit()

        print("Admin created successfully!")
        print("Admin ID:", admin.user_id)
        print("Admin email:", admin.email)

except Exception:
    db.rollback()
    raise

finally:
    db.close()

