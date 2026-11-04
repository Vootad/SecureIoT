from fastapi import Depends, HTTPException
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from sqlalchemy.orm import Session

from auth_token import decode_access_token
from database import get_db
from models import User

# Extract bearer tokens from the Authorization header.
security = HTTPBearer()


def get_current_user(
    credentials: HTTPAuthorizationCredentials = Depends(security),
    db: Session = Depends(get_db)
):
    # Extract the token from the Authorization header.
    token = credentials.credentials

    # Decode and validate the token.
    token_data = decode_access_token(token)

    # Reject requests with invalid or expired tokens.
    if token_data is None:
        raise HTTPException(
            status_code=401,
            detail="Invalid or expired token"
        )

    # Decode and validate the token.
    user = db.query(User).filter(
        User.username == token_data["username"]
    ).first()

    # Reject requests with invalid or expired tokens.
    if user is None or not user.is_active:
        raise HTTPException(
            status_code=401,
            detail="User not found or inactive"
        )

    return user


def get_current_admin(
    current_user: User = Depends(get_current_user)
):
    # Allow access only to users with the admin role.
    if current_user.role != "admin":
        raise HTTPException(
            status_code=403,
            detail="Admin privileges required"
        )

    return current_user
