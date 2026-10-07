from fastapi import FastAPI, Depends, HTTPException, Request
from fastapi.exceptions import RequestValidationError
from fastapi.responses import JSONResponse
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials

from pydantic import BaseModel, Field
from sqlalchemy.orm import Session

from database import engine, Base, get_db
from models import User, Lock, UsedNonce
from security import verify_password
from auth_token import create_access_token, decode_access_token

import time

# SQLAlchemy convert python models to db tables
Base.metadata.create_all(bind=engine)

app = FastAPI()
security = HTTPBearer()


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


def get_current_user(
    credentials: HTTPAuthorizationCredentials = Depends(security)
):
    # Extract the token from the Authorization header
    token = credentials.credentials

    # Decode and validate the token
    user = decode_access_token(token)

    # Reject the request if the token is invalid
    if user is None:
        raise HTTPException(
            status_code=401,
            detail="Invalid or expired token"
        )

    # Return authenticated user information
    return user


class LoginRequest(BaseModel):
    username: str = Field(min_length=1)
    password: str = Field(min_length=1)


class UnlockRequest(BaseModel):
    lock_id: str = Field(min_length=1)
    lock_password: str = Field(min_length=1)

    # Time when the request was created by the Smart Lock
    timestamp: int

    # Unique value used to prevent replay attacks.
    nonce: str = Field(min_length=16)


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


    # Create an access token for the authenticated user
    access_token = create_access_token(user.username, user.role)
    return {
        "success": True,
        "message": "Authentication successful",
        "username": user.username,
        "role": user.role,
        "access_token": access_token,
        "token_type": "bearer"
    }


@app.post("/lock/unlock")
def unlock(
    request: UnlockRequest,
    db: Session = Depends(get_db),
    current_user: dict = Depends(get_current_user)
):

    # Check whether the request is recent enough(timestamp).
    current_time = int(time.time())

    if abs(current_time - request.timestamp) > 30:
        raise HTTPException(
            status_code=400,
            detail="Request expired"
        )

    # Check whether this nonce has already been used(nonce).
    used_nonce = db.query(UsedNonce).filter(
        UsedNonce.nonce == request.nonce
    ).first()

    if used_nonce is not None:
        raise HTTPException(
            status_code=409,
            detail="Replay attack detected"
        )


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

    # Store the nonce so the same request cannot be used again.
    new_nonce = UsedNonce(
        nonce=request.nonce
    )

    db.add(new_nonce)
    db.commit()

    return {
        "success": True,
        "access": "granted",
        "message": "Door unlocked",
        "lock_id": lock.lock_id,
        "username": current_user["username"]
    }
