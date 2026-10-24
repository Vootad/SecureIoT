
from datetime import datetime, timedelta

from fastapi import APIRouter, Depends, HTTPException, Request
from sqlalchemy.orm import Session

from auth_token import create_access_token
from config import MAX_FAILED_ATTEMPTS, BLOCK_DURATION
from database import get_db
from models import User, LoginAttempt
from schemas import LoginRequest
from security import verify_password
from services.audit import write_audit_log


router = APIRouter()


@router.post("/auth/login")
def login(
    request: LoginRequest,
    http_request: Request,
    db: Session = Depends(get_db)
):
    user = db.query(User).filter(
        User.username == request.username
    ).first()

    # Find the rate-limit record for this username and IP.
    client_ip = http_request.client.host

    attempt_record = db.query(LoginAttempt).filter(
        LoginAttempt.username == request.username,
        LoginAttempt.ip == client_ip
    ).first()

    # Check whether this username and IP are currently blocked.
    if attempt_record and attempt_record.blocked_until is not None:
        if datetime.utcnow() < attempt_record.blocked_until:
            write_audit_log(
                db=db,
                request=http_request,
                event_type="rate_limit",
                result="blocked",
                username=request.username,
                reason="login_username_ip_pair_temporarily_blocked"
            )

            raise HTTPException(
                status_code=429,
                detail="Too many failed login attempts. Try again later."
            )

        # The block has expired, so reset the failed attempts.
        attempt_record.failed_attempts = 0
        attempt_record.blocked_until = None
        db.commit()

    # Reject an unknown username and record the failed login.
    if user is None:
        if attempt_record is None:
            attempt_record = LoginAttempt(
                username=request.username,
                ip=client_ip,
                failed_attempts=1
            )
            db.add(attempt_record)
        else:
            attempt_record.failed_attempts += 1

        # Block this username and IP after too many failures.
        if attempt_record.failed_attempts >= MAX_FAILED_ATTEMPTS:
            attempt_record.blocked_until = (
                datetime.utcnow()
                + timedelta(seconds=BLOCK_DURATION)
            )

        db.commit()

        write_audit_log(
            db=db,
            request=http_request,
            event_type="login",
            result="failure",
            username=request.username,
            reason="user_not_found"
        )

        raise HTTPException(
            status_code=401,
            detail="Invalid username or password"
        )

    # Verify the submitted password.
    if not verify_password(request.password, user.password_hash):
        if attempt_record is None:
            attempt_record = LoginAttempt(
                username=request.username,
                ip=client_ip,
                failed_attempts=1
            )
            db.add(attempt_record)
        else:
            # Increase the number of failed attempts.
            attempt_record.failed_attempts += 1

        # Block this username and IP after too many failures.
        if attempt_record.failed_attempts >= MAX_FAILED_ATTEMPTS:
            attempt_record.blocked_until = (
                datetime.utcnow()
                + timedelta(seconds=BLOCK_DURATION)
            )

        db.commit()

        write_audit_log(
            db=db,
            request=http_request,
            event_type="login",
            result="failure",
            username=user.username,
            reason="invalid_password"
        )

        raise HTTPException(
            status_code=401,
            detail="Invalid username or password"
        )

    # Reset failed login attempts after successful authentication.
    if attempt_record is not None:
        attempt_record.failed_attempts = 0
        attempt_record.blocked_until = None
        db.commit()

    # Record successful authentication.
    write_audit_log(
        db=db,
        request=http_request,
        event_type="login",
        result="success",
        username=user.username,
        reason="authentication_successful"
    )

    # Create an access token for the authenticated user.
    access_token = create_access_token(user.username, user.role)

    return {
        "success": True,
        "message": "Authentication successful",
        "username": user.username,
        "role": user.role,
        "access_token": access_token,
        "token_type": "bearer"
    }
