from fastapi import FastAPI
from pydantic import BaseModel
from sqlalchemy.orm import Session


from database import engine, Base
# import models
from models import User
from security import verify_password

Base.metadata.create_all(bind=engine)

app = FastAPI()


class LoginRequest(BaseModel):
    username: str
    password: str



@app.get("/health")
def health():
    return {"status": "ok"}


@app.post("/auth/login")
def login(request: LoginRequest):
    db = Session(bind=engine)

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

    db.close()

    return {
        "success": True,
        "message": "Authentication successful",
        "username": user.username,
        "role": user.role
    }


@app.post("/lock/unlock")
def unlock():
    return {"message": "Unlock endpoint"}
