from fastapi import FastAPI, Depends, HTTPException, Request
from fastapi.exceptions import RequestValidationError
from fastapi.responses import JSONResponse
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials

from pydantic import BaseModel, Field
from sqlalchemy.orm import Session

from database import engine, Base, get_db
from models import User, Lock, UsedNonce, UnlockAttempt
from security import verify_password
from auth_token import create_access_token, decode_access_token

import time
from datetime import datetime, timedelta

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


MAX_FAILED_ATTEMPTS = 5
BLOCK_DURATION = 60


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

    # Find lock
    lock = db.query(Lock).filter(
        Lock.lock_id == request.lock_id
    ).first()

    if lock is None:
        raise HTTPException(
            status_code=401,
            detail="Invalid lock credentials"
        )

    # Find the rate-limit record for this user and lock.
    attempt_record = db.query(UnlockAttempt).filter(
        UnlockAttempt.username == current_user["username"],
        UnlockAttempt.lock_id == request.lock_id
    ).first()

    # Check whether this user is currently blocked.
    if attempt_record and attempt_record.blocked_until is not None:

        if datetime.utcnow() < attempt_record.blocked_until:
            raise HTTPException(
                status_code=429,
                detail="Too many failed attempts. Try again later."
            )

        # The block has expired, so reset the failed attempts.
        attempt_record.failed_attempts = 0
        attempt_record.blocked_until = None

    if not verify_password(
        request.lock_password,
        lock.password_hash
    ):
        # Create a new rate-limit record if this is
        # the first failed attempt for this user and lock.
        if attempt_record is None:
            attempt_record = UnlockAttempt(
                username=current_user["username"],
                lock_id=request.lock_id,
                failed_attempts=1
            )

            db.add(attempt_record)

        else:
            # Increase the number of consecutive failed attempts.
            attempt_record.failed_attempts += 1

        # Block the user after reaching the maximum
        # number of failed attempts.
        if attempt_record.failed_attempts >= MAX_FAILED_ATTEMPTS:
            attempt_record.blocked_until = (
                datetime.utcnow()
                + timedelta(seconds=BLOCK_DURATION)
            )

        # Save the failed attempt before returning the error.
        db.commit()

        # If the limit was reached, return 429.
        if attempt_record.failed_attempts >= MAX_FAILED_ATTEMPTS:
            raise HTTPException(
                status_code=429,
                detail="Too many failed attempts. Try again later."
            )

        # Normal invalid-password response.
        raise HTTPException(
            status_code=401,
            detail="Invalid lock credentials"
        )

    # Reset failed attempts after a successful unlock.
    if attempt_record is not None:
        attempt_record.failed_attempts = 0
        attempt_record.blocked_until = None

    # Store the nonce so the same request cannot be used again.
    new_nonce = UsedNonce(nonce=request.nonce)

    db.add(new_nonce)
    db.commit()

    return {
        "success": True,
        "access": "granted",
        "message": "Door unlocked",
        "lock_id": lock.lock_id,
        "username": current_user["username"]
    }
