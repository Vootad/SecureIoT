
from database import SessionLocal
from models import User
from security import hash_password

# Open a database session.
db = SessionLocal()

try:
    # Check whether bob already exists.
    existing_user = (
        db.query(User)
        .filter(User.username == "bob")
        .first()
    )

    if existing_user:
        print("User 'bob' already exists.")
    else:
        # Store a hashed password, not the plain password.
        new_user = User(
            username="bob",
            password_hash=hash_password("bob12345"),
            role="user"
        )

        db.add(new_user)
        db.commit()

        print("User 'bob' created successfully.")

finally:
    # Always close the database session.
    db.close()
