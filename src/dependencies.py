
from fastapi import Depends, HTTPException
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials

from auth_token import decode_access_token


# Extract bearer tokens from the Authorization header.
security = HTTPBearer()


def get_current_user(
    credentials: HTTPAuthorizationCredentials = Depends(security)
):
    # Extract the token from the Authorization header.
    token = credentials.credentials

    # Decode and validate the token.
    user = decode_access_token(token)

    # Reject requests with invalid or expired tokens.
    if user is None:
        raise HTTPException(
            status_code=401,
            detail="Invalid or expired token"
        )

    return user
