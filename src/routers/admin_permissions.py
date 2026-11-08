from fastapi import APIRouter, Depends, HTTPException, Response
from sqlalchemy.orm import Session
from sqlalchemy.exc import IntegrityError

from database import get_db
from dependencies import get_current_admin
from models import User, Lock, UserLockPermission
from schemas import UserLockPermissionResponse


router = APIRouter(
    prefix="/admin/users",
    tags=["Admin - User Permissions"]
)


@router.post(
    "/{user_id}/locks/{lock_db_id}",
    response_model=UserLockPermissionResponse,
    status_code=201
)
def assign_lock_permission(
    user_id: int,
    lock_db_id: int,
    admin: User = Depends(get_current_admin),
    db: Session = Depends(get_db)
):
    # Check whether the user exists.
    user = db.query(User).filter(User.id == user_id).first()

    if user is None:
        raise HTTPException(
            status_code=404,
            detail="User not found"
        )

    # Check whether the lock exists.
    lock = db.query(Lock).filter(Lock.id == lock_db_id).first()

    if lock is None:
        raise HTTPException(
            status_code=404,
            detail="Lock not found"
        )

    # Prevent duplicate permissions.
    existing_permission = db.query(UserLockPermission).filter(
        UserLockPermission.user_id == user_id,
        UserLockPermission.lock_id == lock_db_id
    ).first()

    if existing_permission:
        raise HTTPException(
            status_code=409,
            detail="Permission already exists"
        )

    # Create a new permission.
    permission = UserLockPermission(
        user_id=user_id,
        lock_id=lock_db_id
    )

    try:
        db.add(permission)
        db.commit()
        db.refresh(permission)

    except IntegrityError:
        db.rollback()
        raise HTTPException(
            status_code=409,
            detail="Permission already exists"
        )

    return permission


@router.get(
    "/{user_id}/locks",
    response_model=list[UserLockPermissionResponse]
)
def get_user_lock_permissions(
    user_id: int,
    admin: User = Depends(get_current_admin),
    db: Session = Depends(get_db)
):
    # Make sure the requested user exists.
    user = db.query(User).filter(User.id == user_id).first()

    if user is None:
        raise HTTPException(
            status_code=404,
            detail="User not found"
        )

    # Retrieve all permissions assigned to this user.
    permissions = db.query(UserLockPermission).filter(
        UserLockPermission.user_id == user_id
    ).order_by(UserLockPermission.id).all()

    return permissions


@router.delete(
    "/{user_id}/locks/{lock_db_id}",
    status_code=204
)
def revoke_lock_permission(
    user_id: int,
    lock_db_id: int,
    admin: User = Depends(get_current_admin),
    db: Session = Depends(get_db)
):
    # Check whether the user exists.
    user = db.query(User).filter(User.id == user_id).first()

    if user is None:
        raise HTTPException(
            status_code=404,
            detail="User not found"
        )

    # Find the permission to revoke.
    permission = db.query(UserLockPermission).filter(
        UserLockPermission.user_id == user_id,
        UserLockPermission.lock_id == lock_db_id
    ).first()

    if permission is None:
        raise HTTPException(
            status_code=404,
            detail="Permission not found"
        )

    # Delete the permission.
    db.delete(permission)
    db.commit()

    return Response(status_code=204)
