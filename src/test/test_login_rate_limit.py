import requests
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parents[2]
CERT_PATH = PROJECT_ROOT / "certs" / "server.crt"

SERVER_URL = "https://127.0.0.1:8000"

# Test credentials
USERNAME = "alice"
CORRECT_PASSWORD = "123456"
WRONG_PASSWORD = "wrong_password"

MAX_FAILED_ATTEMPTS = 5


def attempt_login(username, password):
    """Send one login request."""

    return requests.post(
        f"{SERVER_URL}/auth/login",
        json={
            "username": username,
            "password": password
        },
        verify=str(CERT_PATH),
        timeout=5
    )


def main():
    print("Testing Login Rate Limiting...")
    print(f"Username: {USERNAME}")
    print(f"Maximum failed attempts: {MAX_FAILED_ATTEMPTS}")

    print("\nSending incorrect passwords...")

    # Send five failed login attempts.
    for attempt in range(1, MAX_FAILED_ATTEMPTS + 1):
        response = attempt_login(
            USERNAME,
            WRONG_PASSWORD
        )

        print(
            f"Attempt {attempt}: "
            f"HTTP {response.status_code} - "
            f"{response.text}"
        )

        if response.status_code != 401:
            print(
                "WARNING: Expected HTTP 401 "
                "for an incorrect password."
            )
            return

    print("\nTesting correct password while blocked...")

    # The correct password should still be rejected
    # while the username and IP are blocked.
    response = attempt_login(
        USERNAME,
        CORRECT_PASSWORD
    )

    print(
        f"Correct password while blocked: "
        f"HTTP {response.status_code} - "
        f"{response.text}"
    )

    if response.status_code == 429:
        print("\nPASS: Login rate limiting is working.")
    else:
        print(
            "\nFAIL: Expected HTTP 429 "
            "while the account/IP pair is blocked."
        )


if __name__ == "__main__":
    main()
