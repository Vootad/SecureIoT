import time
from datetime import datetime, timedelta

from fastapi import APIRouter, Depends, HTTPException, Request
from sqlalchemy.orm import Session

from config import MAX_FAILED_ATTEMPTS, BLOCK_DURATION
from database import get_db
from dependencies import get_current_user
from models import Lock, UsedNonce, UnlockAttempt
from schemas import UnlockRequest
from security import verify_password
from services.audit import write_audit_log


# Create a separate router for Smart Lock operations.
router = APIRouter()


def cleanup_expired_nonces(db: Session) -> int:
    """Delete nonce records older than 90 seconds."""

    # Calculate the cutoff time using the server's UTC clock.
    cutoff_time = datetime.utcnow() - timedelta(seconds=90)

    # Delete nonce records that are older than the cutoff.
    deleted_count = (
        db.query(UsedNonce)
        .filter(UsedNonce.created_at < cutoff_time)
        .delete(synchronize_session=False)
    )

    # Save the deletion to the database.
    db.commit()

    # Return the number of deleted records.
    return deleted_count


@router.post("/lock/unlock")
def unlock(
    request: UnlockRequest,
    http_request: Request,
    db: Session = Depends(get_db),
    current_user: dict = Depends(get_current_user)
):
    # Check whether the request timestamp is within the allowed 30-second window.
    current_time = int(time.time())

    if abs(current_time - request.timestamp) > 30:
        write_audit_log(
            db=db,
            request=http_request,
            event_type="unlock",
            result="denied",
            username=current_user["username"],
            reason="request_expired"
        )

        raise HTTPException(
            status_code=400,
            detail="Request expired"
        )

    # Remove old nonce records before checking for replay attempts.
    cleanup_expired_nonces(db)

    # Reject a nonce that has already been used.
    used_nonce = db.query(UsedNonce).filter(
        UsedNonce.nonce == request.nonce
    ).first()

    if used_nonce is not None:
        write_audit_log(
            db=db,
            request=http_request,
            event_type="replay_attempt",
            result="denied",
            username=current_user["username"],
            reason="duplicate_nonce"
        )

        raise HTTPException(
            status_code=409,
            detail="Replay attack detected"
        )

    # Find the requested lock in the database.
    lock = db.query(Lock).filter(
        Lock.lock_id == request.lock_id
    ).first()

    if lock is None:
        write_audit_log(
            db=db,
            request=http_request,
            event_type="unlock",
            result="denied",
            username=current_user["username"],
            reason="lock_not_found"
        )

        raise HTTPException(
            status_code=401,
            detail="Invalid lock credentials"
        )

    # Find the failed-attempt record for this user and lock.
    attempt_record = db.query(UnlockAttempt).filter(
        UnlockAttempt.username == current_user["username"],
        UnlockAttempt.lock_id == request.lock_id
    ).first()

    # Reject requests while this user-lock pair is temporarily blocked.
    if attempt_record and attempt_record.blocked_until is not None:
        if datetime.utcnow() < attempt_record.blocked_until:
            write_audit_log(
                db=db,
                request=http_request,
                event_type="rate_limit",
                result="blocked",
                username=current_user["username"],
                reason="account_lock_pair_temporarily_blocked"
            )

            raise HTTPException(
                status_code=429,
                detail="Too many failed attempts. Try again later."
            )

        # Reset the counter when the temporary block has expired.
        attempt_record.failed_attempts = 0
        attempt_record.blocked_until = None

    # Verify the submitted lock password.
    if not verify_password(
        request.lock_password,
        lock.password_hash
    ):
        # Create a record for the first failed attempt.
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

        # Temporarily block this user-lock pair after the limit is reached.
        if attempt_record.failed_attempts >= MAX_FAILED_ATTEMPTS:
            attempt_record.blocked_until = (
                datetime.utcnow()
                + timedelta(seconds=BLOCK_DURATION)
            )

        # Save the failed-attempt counter before returning an error.
        db.commit()

        # Record the rejected unlock request in the audit log.
        write_audit_log(
            db=db,
            request=http_request,
            event_type="unlock",
            result="denied",
            username=current_user["username"],
            reason="invalid_lock_password"
        )

        # Return 429 when the maximum number of failed attempts is reached.
        if attempt_record.failed_attempts >= MAX_FAILED_ATTEMPTS:
            write_audit_log(
                db=db,
                request=http_request,
                event_type="rate_limit",
                result="blocked",
                username=current_user["username"],
                reason="maximum_failed_attempts_reached"
            )

            raise HTTPException(
                status_code=429,
                detail="Too many failed attempts. Try again later."
            )

        # Return 401 for an incorrect password below the limit.
        raise HTTPException(
            status_code=401,
            detail="Invalid lock credentials"
        )

    # Reset the failed-attempt counter after successful password verification.
    if attempt_record is not None:
        attempt_record.failed_attempts = 0
        attempt_record.blocked_until = None

    # Save the nonce so the same request cannot be accepted again.
    new_nonce = UsedNonce(nonce=request.nonce)
    db.add(new_nonce)
    db.commit()

    # Record the successful unlock operation.
    write_audit_log(
        db=db,
        request=http_request,
        event_type="unlock",
        result="success",
        username=current_user["username"],
        reason="valid_lock_credentials"
    )

    # Return the access decision and relevant identifiers.
    return {
        "success": True,
        "access": "granted",
        "message": "Door unlocked",
        "lock_id": lock.lock_id,
        "username": current_user["username"]
    }
