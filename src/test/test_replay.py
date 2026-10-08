import time
import secrets
import requests

# Server address
SERVER_URL = "https://127.0.0.1:8000"

# Server certificate
CERT_PATH = "../../certs/server.crt"

# Login information
USERNAME = "alice"
PASSWORD = "123456"

# Lock information
LOCK_ID = "lock_001"
LOCK_PASSWORD = "987654"


# Step 1: Login and receive an access token
login_response = requests.post(
    f"{SERVER_URL}/auth/login",
    json={
        "username": USERNAME,
        "password": PASSWORD
    },
    verify=CERT_PATH
)

print("Login status:", login_response.status_code)

access_token = login_response.json()["access_token"]

# Create one unlock request.
# The same request will be sent twice.
request_data = {
    "lock_id": LOCK_ID,
    "lock_password": LOCK_PASSWORD,

    # Current Unix timestamp
    "timestamp": int(time.time()),

    # Generate one unique nonce
    "nonce": secrets.token_urlsafe(16)
}

headers = {
    "Authorization": f"Bearer {access_token}"
}


# Step 2: Send the request for the first time
print("\n--- First request ---")

response1 = requests.post(
    f"{SERVER_URL}/lock/unlock",
    json=request_data,
    headers=headers,
    verify=CERT_PATH
)

print("Status:", response1.status_code)
print("Response:", response1.text)


# Step 3: Send EXACTLY the same request again
print("\n--- Second request (Replay) ---")

response2 = requests.post(
    f"{SERVER_URL}/lock/unlock",
    json=request_data,
    headers=headers,
    verify=CERT_PATH
)

print("Status:", response2.status_code)
print("Response:", response2.text)
