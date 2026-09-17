from database import SessionLocal
from models import Lock
from security import hash_password


db = SessionLocal()

lock = Lock(
    lock_id="lock_001",
    password_hash=hash_password("987654")
)

db.add(lock)
db.commit()
db.refresh(lock)

print("Lock created successfully!")
print("Lock ID:", lock.lock_id)
print("Password hash:", lock.password_hash)

db.close()
