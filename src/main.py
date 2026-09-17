from fastapi import FastAPI, Depends, HTTPException, Request
from fastapi.exceptions import RequestValidationError
from fastapi.responses import JSONResponse

from pydantic import BaseModel, Field
from sqlalchemy.orm import Session

from database import engine, Base, get_db
from models import User, Lock
from security import verify_password

Base.metadata.create_all(bind=engine)

app = FastAPI()

# Exception handler
@app.exception_handler(RequestValidationError)
async def validation_exception_handler(
    request: Request,
    exc: RequestValidationError
):
    return JSONResponse(
        status_code=422,
        content={
            "success": False,
            "error": "Validation Error",
            "message": "Invalid request data",
            "details": exc.errors()
        }
    )


class LoginRequest(BaseModel):
    username: str = Field(min_length=1)
    password: str = Field(min_length=1)


class UnlockRequest(BaseModel):
    lock_id: str = Field(min_length=1)
    lock_password: str = Field(min_length=1)


@app.get("/health")
def health():
    return {"status": "ok"}


@app.post("/auth/login")
def login(request: LoginRequest, db: Session = Depends(get_db)):

    user = db.query(User).filter(
        User.username == request.username
    ).first()

    if user is None:
        raise HTTPException(
            status_code=401,
            detail="Invalid username or password"
        )

    if not verify_password(request.password, user.password_hash):
        raise HTTPException(
            status_code=401,
            detail="Invalid username or password"
        )


    return {
        "success": True,
        "message": "Authentication successful",
        "username": user.username,
        "role": user.role
    }


@app.post("/lock/unlock")
def unlock(
    request: UnlockRequest,
    db: Session = Depends(get_db)
):
    lock = db.query(Lock).filter(
        Lock.lock_id == request.lock_id
    ).first()

    if lock is None:
        raise HTTPException(
            status_code=401,
            detail="Invalid lock credentials"
        )

    if not verify_password(
        request.lock_password,
        lock.password_hash
    ):
        raise HTTPException(
            status_code=401,
            detail="Invalid lock credentials"
        )

    return {
        "success": True,
        "access": "granted",
        "message": "Door unlocked",
        "lock_id": lock.lock_id
    }
