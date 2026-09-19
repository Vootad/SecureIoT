import requests


SERVER_URL = "http://127.0.0.1:8000"


def login(username, password):
    """Authenticate the user and return the access token."""

    response = requests.post(
        f"{SERVER_URL}/auth/login",
        json={
            "username": username,
            "password": password
        }
    )

    if response.status_code != 200:
        print("Login failed.")
        print(response.json())
        return None

    data = response.json()

    print("Login successful.")

    return data["access_token"]


def unlock_lock(access_token, lock_id, lock_password):
    """Send an unlock request to the server."""

    response = requests.post(
        f"{SERVER_URL}/lock/unlock",
        json={
            "lock_id": lock_id,
            "lock_password": lock_password
        },
        headers={
            "Authorization": f"Bearer {access_token}"
        }
    )

    return response


def main():
    print("=====================")
    print("      SMART LOCK")
    print("=====================")

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

    if response.status_code == 200:
        data = response.json()

        print("\nAccess Granted")
        print(data["message"])

    else:
        print("\nAccess Denied")
        print(response.json()["detail"])


if __name__ == "__main__":
    main()