from fastapi import FastAPI, Depends
from pydantic import BaseModel, Field
from sqlalchemy.orm import Session

from database import engine, Base, get_db
from models import User
from security import verify_password

Base.metadata.create_all(bind=engine)

app = FastAPI()


class LoginRequest(BaseModel):
    username: str = Field(min_length=1)
    password: str = Field(min_length=1)



@app.get("/health")
def health():
    return {"status": "ok"}


@app.post("/auth/login")
def login(request: LoginRequest, db: Session = Depends(get_db)):

    user = db.query(User).filter(
        User.username == request.username
    ).first()

    if user is None:
        db.close()
        return {
            "success": False,
            "message": "Invalid username or password"
        }

    if not verify_password(request.password, user.password_hash):
        db.close()
        return {
            "success": False,
            "message": "Invalid username or password"
        }


    return {
        "success": True,
        "message": "Authentication successful",
        "username": user.username,
        "role": user.role
    }


@app.post("/lock/unlock")
def unlock():
    return {"message": "Unlock endpoint"}
