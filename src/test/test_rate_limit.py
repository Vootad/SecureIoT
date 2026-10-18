import requests
import secrets
import time

# Server configuration
SERVER_URL = "https://127.0.0.1:8000"
CERT_PATH = "../../certs/server.crt"

# Test credentials
USERNAME = "alice"
USER_PASSWORD = "123456"

LOCK_ID = "lock_001"
WRONG_LOCK_PASSWORD = "wrong_password"
CORRECT_LOCK_PASSWORD = "987654"


def login(username, password):
    """Log in and return the access token."""

    response = requests.post(
        f"{SERVER_URL}/auth/login",
        json={
            "username": username,
            "password": password
        },
        verify=CERT_PATH,
        timeout=5
    )

    response.raise_for_status()
    return response.json()["access_token"]


def attempt_unlock(token, lock_password):
    """Send one unlock request."""

    response = requests.post(
        f"{SERVER_URL}/lock/unlock",
        json={
            "lock_id": LOCK_ID,
            "lock_password": lock_password,
            "timestamp": int(time.time()),
            "nonce": secrets.token_urlsafe(16)
        },
        headers={
            "Authorization": f"Bearer {token}"
        },
        verify=CERT_PATH,
        timeout=5
    )

    return response


def main():
    # Authenticate Alice.
    alice_token = login(USERNAME, USER_PASSWORD)

    print("Testing five incorrect lock passwords...")

    for attempt in range(1, 6):
        response = attempt_unlock(
            alice_token,
            WRONG_LOCK_PASSWORD
        )

        print(
            f"Attempt {attempt}: "
            f"HTTP {response.status_code} - "
            f"{response.text}"
        )

    # A correct password should still be rejected while blocked.
    response = attempt_unlock(
        alice_token,
        CORRECT_LOCK_PASSWORD
    )

    print("\nCorrect password while blocked:")
    print(f"HTTP {response.status_code} - {response.text}")


    # Test whether bob can access the lock while alice is blocked.
    print("\nTesting bob while alice is blocked...")


    # Log bob in to obtain his own access token.
    bob_login_response = requests.post(
        f"{SERVER_URL}/auth/login",
        json={
            "username": "bob",
            "password": "bob12345"
        },
        verify=CERT_PATH
    )

    print(f"Bob login: HTTP {bob_login_response.status_code}")

    if bob_login_response.status_code == 200:
        bob_token = bob_login_response.json()["access_token"]

        # Create a fresh timestamp and nonce for bob's request.
        bob_payload = {
            "lock_id": "lock_001",
            "lock_password": "987654",
            "timestamp": int(time.time()),
            "nonce": secrets.token_urlsafe(16)
        }

        bob_unlock_response = requests.post(
            f"{SERVER_URL}/lock/unlock",
            json=bob_payload,
            headers={
                "Authorization": f"Bearer {bob_token}"
            },
            verify=CERT_PATH
        )

        print(
            f"Bob unlock attempt: "
            f"HTTP {bob_unlock_response.status_code}"
        )
        print(bob_unlock_response.text)


if __name__ == "__main__":
    main()
