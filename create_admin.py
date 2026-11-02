
import bcrypt
from getpass import getpass

from database import sessionLocal
from routes.admin.admin_model import Admin


db = sessionLocal()

try:
    email = input("Enter admin email: ").strip().lower()
    password = getpass("Enter admin password: ")
    name = input("Enter admin name: ").strip()
    phone = input("Enter admin phone (optional): ").strip() or None

    if not email or not password or not name:
        raise ValueError("Name, email, and password are required.")

    if len(password) < 8:
        raise ValueError("Password must contain at least 8 characters.")

    existing_admin = (
        db.query(Admin)
        .filter(Admin.email == email)
        .first()
    )

    if existing_admin:
        print("This admin email already exists.")
    else:
        hashed_password = bcrypt.hashpw(
            password.encode("utf-8"),
            bcrypt.gensalt()
        ).decode("utf-8")

        admin = Admin(
            name=name,
            email=email,
            phone=phone,
            password_hash=hashed_password,
            is_active=True
        )

        db.add(admin)
        db.commit()
        db.refresh(admin)

        print("Admin created successfully!")
        print("Admin ID:", admin.admin_id)
        print("Admin email:", admin.email)

except Exception:
    db.rollback()
    raise

finally:
    db.close()
