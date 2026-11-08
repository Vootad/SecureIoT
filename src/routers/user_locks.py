
from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from database import get_db
from dependencies import get_current_user
from models import Lock, User, UserLockPermission


router = APIRouter(
    prefix="/user/locks",
    tags=["User - Locks"]
)


@router.get("/")
def get_user_locks(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    # Retrieve locks assigned to the authenticated user.
    locks = (
        db.query(Lock)
        .join(
            UserLockPermission,
            UserLockPermission.lock_id == Lock.id
        )
        .filter(
            UserLockPermission.user_id == current_user.id
        )
        .order_by(Lock.id)
        .all()
    )

    # Return only public lock information.
    return [
        {
            "id": lock.id,
            "lock_id": lock.lock_id,
            "is_active": bool(lock.is_active)
        }
        for lock in locks
    ]
