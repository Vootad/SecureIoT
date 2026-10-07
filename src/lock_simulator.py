import requests
from pathlib import Path
import time
import secrets


SERVER_URL = "https://127.0.0.1:8000"

# Path to the server certificate used to verify the TLS connection.
CERT_PATH = Path(__file__).resolve().parent.parent / "certs" / "server.crt"


def check_server_connection():
    """Check whether the FastAPI server is available."""

    try:
        response = requests.get(
            f"{SERVER_URL}/health",
            verify=CERT_PATH,
            timeout=5
        )

        if response.status_code == 200:
            return True

        return False

    except requests.RequestException:
        return False


def login(username, password):
    """Authenticate the user and return the access token."""

    try:
        response = requests.post(
            f"{SERVER_URL}/auth/login",
            json={
                "username": username,
                "password": password
            },
            verify=CERT_PATH,
            # client wait for just 5 sec
            timeout=5
        )

    except requests.RequestException:
        print("Unable to connect to the server")
        return None

    if response.status_code != 200:
        print("Login failed.")

        try:
            print(response.json())
        except (ValueError, KeyError):
            print("Server returned an unexpected response")

        return None

    data = response.json()

    print("Login successful.")

    return data["access_token"]


def unlock_lock(access_token, lock_id, lock_password):
    """Send an unlock request to the server."""

    try:
        # create timestamp
        timestamp = int(time.time())

        # generate a uniqie random value
        nonce = secrets.token_urlsafe(16)

        response = requests.post(
            f"{SERVER_URL}/lock/unlock",
            json={
                "lock_id": lock_id,
                "lock_password": lock_password,
                "timestamp": timestamp,
                "nonce": nonce
            },
            headers={
                "Authorization": f"Bearer {access_token}"
            },
            # Verify the server certificate during the TLS connection.
            verify=CERT_PATH,
            timeout=5
        )
    except requests.RequestException:
        print("Unable to connect to the server")
        return None

    return response


def main():
    print("=====================")
    print("      SMART LOCK")
    print("=====================")

    print("\nChecking server connection...")

    if not check_server_connection():
        print("Unable to connect to the server")
        print("Please make sure the server is running")
        return

    print("Server connection successful")
    username = input("Username: ")
    password = input("Password: ")

    print("\nAuthenticating...")

    access_token = login(username, password)

    if access_token is None:
        return

    print("Authentication successful.")

    lock_id = input("\nEnter Lock ID: ")
    lock_password = input("Enter Unlock Code: ")

    print("\nSending unlock request...")

    response = unlock_lock(
        access_token,
        lock_id,
        lock_password
    )

    if response is None:
        return

    if response.status_code == 200:
        data = response.json()

        print("\nAccess Granted")
        print(data["message"])

    else:
        print("\nAccess Denied")

        try:
            print(response.json()["detail"])
        except (ValueError, KeyError):
            print("Server returned an unexpected response.")


if __name__ == "__main__":
    main()
