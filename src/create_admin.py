from datetime import datetime

from database import SessionLocal
from models import User
from security import hash_password


db = SessionLocal()

try:
    # Check whether an administrator already exists.
    existing_admin = db.query(User).filter(
        User.role == "admin"
    ).first()

    if existing_admin:
        print("An administrator already exists.")

    else:
        # Create the initial administrator.
        admin = User(
            username="admin",
            password_hash=hash_password("admin1"),
            role="admin",
            is_active=1,
            created_at=datetime.utcnow()
        )

        db.add(admin)
        db.commit()

        print("Administrator created successfully!")

finally:
    db.close()
