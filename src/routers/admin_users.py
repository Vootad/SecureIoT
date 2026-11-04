
from datetime import datetime

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from sqlalchemy.exc import IntegrityError

from database import get_db
from models import User
from security import hash_password
from dependencies import get_current_admin
from schemas import (
    AdminUserCreate,
    AdminUserResponse,
    UserStatusUpdate
)


router = APIRouter(
    prefix="/admin/users",
    tags=["Admin - Users"]
)


@router.post("/", response_model=AdminUserResponse, status_code=201)
def create_user(
    request: AdminUserCreate,
    admin: User = Depends(get_current_admin),
    db: Session = Depends(get_db)
):
    # Check whether the username already exists.
    existing_user = db.query(User).filter(
        User.username == request.username
    ).first()

    if existing_user:
        raise HTTPException(
            status_code=409,
            detail="Username already exists"
        )

    # Create a regular user with a hashed password.
    new_user = User(
        username=request.username,
        password_hash=hash_password(request.password),
        role="user",
        is_active=1,
        created_at=datetime.utcnow()
    )

    try:
        db.add(new_user)
        db.commit()
        db.refresh(new_user)

    except IntegrityError:
        # Handle possible duplicate usernames caused by concurrent requests.
        db.rollback()

        raise HTTPException(
            status_code=409,
            detail="Username already exists"
        )

    return new_user


@router.get("/", response_model=list[AdminUserResponse])
def get_users(
    admin: User = Depends(get_current_admin),
    db: Session = Depends(get_db)
):
    # Retrieve all users without exposing password hashes.
    users = db.query(User).order_by(User.id).all()

    return users


@router.patch("/{user_id}/status", response_model=AdminUserResponse)
def update_user_status(
    user_id: int,
    request: UserStatusUpdate,
    admin: User = Depends(get_current_admin),
    db: Session = Depends(get_db)
):
    # Find the target user.
    user = db.query(User).filter(
        User.id == user_id
    ).first()

    if user is None:
        raise HTTPException(
            status_code=404,
            detail="User not found"
        )

    # Administrators must always remain active.
    if user.role == "admin":
        raise HTTPException(
            status_code=403,
            detail="Administrator status cannot be changed"
        )

    # Update the user's activation status.
    user.is_active = int(request.is_active)

    db.commit()
    db.refresh(user)

    return user
