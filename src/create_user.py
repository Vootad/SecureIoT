from database import SessionLocal
from models import User
from security import hash_password


db = SessionLocal()

user = User(
    username="alice",
    password_hash=hash_password("123456"),
    role="user"
)

db.add(user)
db.commit()
db.refresh(user)

print("User created successfully!")
print("Username:", user.username)
print("Password hash:", user.password_hash)

db.close()
