from datetime import datetime, timedelta, timezone

from jose import jwt, JWTError


SECRET_KEY = "change-this-secret-key"
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 30


def create_access_token(username: str, role: str):
    # Set the token expiration time
    expire = datetime.now(timezone.utc) + timedelta(
        minutes=ACCESS_TOKEN_EXPIRE_MINUTES
    )

    # Store user information inside the token
    payload = {
        "sub": username,
        "role": role,
        "exp": expire
    }

    # Create and return the JWT token
    return jwt.encode(
        payload,
        SECRET_KEY,
        algorithm=ALGORITHM
    )


def decode_access_token(token: str):
    try:
        payload = jwt.decode(
            token,
            SECRET_KEY,
            algorithms=[ALGORITHM]
        )

        username = payload.get("sub")
        role = payload.get("role")

        # Both username and role are required
        if username is None or role is None:
            return None

        return {
            "username": username,
            "role": role
        }

    # when token is invalid
    except JWTError:
        return None
