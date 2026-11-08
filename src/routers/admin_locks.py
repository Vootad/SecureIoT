from datetime import datetime

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from sqlalchemy.exc import IntegrityError

from database import get_db
from dependencies import get_current_admin
from models import Lock, User
from schemas import AdminLockCreate, AdminLockResponse, LockStatusUpdate
from security import hash_password


# Create a separate router for admin lock operations.
router = APIRouter(
    prefix="/admin/locks",
    tags=["Admin - Locks"]
)


@router.post("/", response_model=AdminLockResponse, status_code=201)
def create_lock(
    request: AdminLockCreate,
    admin: User = Depends(get_current_admin),
    db: Session = Depends(get_db)
):
    # Check whether the lock identifier already exists.
    existing_lock = db.query(Lock).filter(
        Lock.lock_id == request.lock_id
    ).first()

    if existing_lock:
        raise HTTPException(
            status_code=409,
            detail="Lock identifier already exists"
        )

    # Create a new lock with a hashed password.
    new_lock = Lock(
        lock_id=request.lock_id,
        password_hash=hash_password(request.password),
        is_active=1,
        created_at=datetime.utcnow()
    )

    try:
        db.add(new_lock)
        db.commit()
        db.refresh(new_lock)

    except IntegrityError:
        # Roll back the transaction if a duplicate ID is detected.
        db.rollback()

        raise HTTPException(
            status_code=409,
            detail="Lock identifier already exists"
        )

    return new_lock


@router.get("/", response_model=list[AdminLockResponse])
def get_locks(
    admin: User = Depends(get_current_admin),
    db: Session = Depends(get_db)
):
    # Retrieve all locks ordered by their database ID.
    locks = db.query(Lock).order_by(Lock.id).all()

    return locks


@router.patch("/{lock_id}/status", response_model=AdminLockResponse)
def update_lock_status(
    lock_id: int,
    request: LockStatusUpdate,
    admin: User = Depends(get_current_admin),
    db: Session = Depends(get_db)
):
    # Find the lock using its database ID.
    lock = db.query(Lock).filter(
        Lock.id == lock_id
    ).first()

    if lock is None:
        raise HTTPException(
            status_code=404,
            detail="Lock not found"
        )

    # Update the lock's active status.
    lock.is_active = int(request.is_active)

    db.commit()
    db.refresh(lock)

    return lock
