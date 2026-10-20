import requests
import time
import secrets
from database import SessionLocal
from models import AuditLog, UnlockAttempt
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parents[2]
CERT_PATH = PROJECT_ROOT / "certs" / "server.crt"


# Server configuration
SERVER_URL = "https://127.0.0.1:8000"
# CERT_PATH = "../certs/server.crt"

# Test credentials
USERNAME = "alice"
WRONG_PASSWORD = "definitely_wrong_password"


def main():
    # Open a database session
    db = SessionLocal()

    try:
        # Send a login request using an incorrect password
        response = requests.post(
            f"{SERVER_URL}/auth/login",
            json={
                "username": USERNAME,
                "password": WRONG_PASSWORD
            },
            verify=CERT_PATH,
            timeout=5
        )

        print("Login HTTP status:", response.status_code)

        # Check whether the failed login was recorded
        audit_log = (
            db.query(AuditLog)
            .filter(
                AuditLog.username == USERNAME,
                AuditLog.event_type == "login",
                AuditLog.result == "failure",
                AuditLog.reason == "invalid_password"
            )
            .order_by(AuditLog.id.desc())
            .first()
        )

        assert response.status_code == 401, (
            f"Expected HTTP 401, got {response.status_code}"
        )

        assert audit_log is not None, (
            "Failed login was not recorded in AuditLog"
        )

        print("PASS: Failed login was recorded in AuditLog")
        print("Event:", audit_log.event_type)
        print("Result:", audit_log.result)
        print("Reason:", audit_log.reason)
        print("IP address:", audit_log.ip_address)



        # Test a successful login using the correct password
        print("\n--- Testing successful login ---")

        response_success = requests.post(
            f"{SERVER_URL}/auth/login",
            json={
                "username": USERNAME,
                "password": "123456"
            },
            verify=CERT_PATH,
            timeout=5
        )

        print("Login HTTP status:", response_success.status_code)

        # Verify that the server returned an access token
        assert response_success.status_code == 200, (
            f"Expected HTTP 200, got {response_success.status_code}"
        )

        assert "access_token" in response_success.json(), (
            "Successful login response does not contain an access token"
        )

        # Check whether the successful login was recorded
        success_log = (
            db.query(AuditLog)
            .filter(
                AuditLog.username == USERNAME,
                AuditLog.event_type == "login",
                AuditLog.result == "success",
                AuditLog.reason == "authentication_successful"
            )
            .order_by(AuditLog.id.desc())
            .first()
        )

        assert success_log is not None, (
            "Successful login was not recorded in AuditLog"
        )

        print("PASS: Successful login was recorded in AuditLog")
        print("Event:", success_log.event_type)
        print("Result:", success_log.result)
        print("Reason:", success_log.reason)



        # Test replay prevention and audit logging
        print("\n--- Testing replay detection ---")

        # Reuse the access token from the successful login test
        access_token = response_success.json()["access_token"]

        # Create one valid unlock request
        request_data = {
            "lock_id": "lock_001",
            "lock_password": "987654",
            "timestamp": int(time.time()),
            "nonce": secrets.token_urlsafe(16)
        }

        headers = {
            "Authorization": f"Bearer {access_token}"
        }

        # Send the original request
        first_response = requests.post(
            f"{SERVER_URL}/lock/unlock",
            json=request_data,
            headers=headers,
            verify=CERT_PATH,
            timeout=5
        )

        print("First request status:", first_response.status_code)

        assert first_response.status_code == 200, (
            "The first unlock request should succeed. "
            f"Got HTTP {first_response.status_code}: "
            f"{first_response.text}"
        )

        # Remember the latest audit log ID before replaying
        latest_log = (
            db.query(AuditLog.id)
            .order_by(AuditLog.id.desc())
            .first()
        )
        previous_log_id = latest_log[0] if latest_log else 0

        # Send exactly the same request again
        replay_response = requests.post(
            f"{SERVER_URL}/lock/unlock",
            json=request_data,
            headers=headers,
            verify=CERT_PATH,
            timeout=5
        )

        print("Replay request status:", replay_response.status_code)

        assert replay_response.status_code == 409, (
            "Replay request should be rejected with HTTP 409. "
            f"Got HTTP {replay_response.status_code}: "
            f"{replay_response.text}"
        )

        # Verify that this replay attempt created a new audit record
        replay_log = (
            db.query(AuditLog)
            .filter(
                AuditLog.id > previous_log_id,
                AuditLog.username == USERNAME,
                AuditLog.event_type == "replay_attempt",
                AuditLog.result == "denied",
                AuditLog.reason == "duplicate_nonce"
            )
            .order_by(AuditLog.id.desc())
            .first()
        )

        assert replay_log is not None, (
            "Replay attempt was rejected but not recorded in AuditLog"
        )

        print("PASS: Replay attempt was recorded in AuditLog")
        print("Event:", replay_log.event_type)
        print("Result:", replay_log.result)
        print("Reason:", replay_log.reason)
        print("IP address:", replay_log.ip_address)



        # Test audit logging for an incorrect lock password
        print("\n--- Testing invalid lock password ---")

        # Record the latest audit log ID before this request
        latest_log = (
            db.query(AuditLog.id)
            .order_by(AuditLog.id.desc())
            .first()
        )
        previous_log_id = latest_log[0] if latest_log else 0

        # Create a new unlock request with an incorrect password
        wrong_password_request = {
            "lock_id": "lock_001",
            "lock_password": "definitely_wrong_lock_password",
            "timestamp": int(time.time()),
            "nonce": secrets.token_urlsafe(16)
        }

        wrong_password_response = requests.post(
            f"{SERVER_URL}/lock/unlock",
            json=wrong_password_request,
            headers=headers,
            verify=CERT_PATH,
            timeout=5
        )

        print(
            "Unlock HTTP status:",
            wrong_password_response.status_code
        )

        # The server should reject the incorrect lock password
        assert wrong_password_response.status_code == 401, (
            "Expected HTTP 401 for an incorrect lock password, "
            f"got {wrong_password_response.status_code}: "
            f"{wrong_password_response.text}"
        )

        # Verify that a new audit record was created for this request
        wrong_password_log = (
            db.query(AuditLog)
            .filter(
                AuditLog.id > previous_log_id,
                AuditLog.username == USERNAME,
                AuditLog.event_type == "unlock",
                AuditLog.result == "denied",
                AuditLog.reason == "invalid_lock_password"
            )
            .order_by(AuditLog.id.desc())
            .first()
        )

        assert wrong_password_log is not None, (
            "Invalid lock password was rejected but not recorded "
            "in AuditLog"
        )

        print("PASS: Invalid lock password was recorded in AuditLog")
        print("Event:", wrong_password_log.event_type)
        print("Result:", wrong_password_log.result)
        print("Reason:", wrong_password_log.reason)
        print("IP address:", wrong_password_log.ip_address)



        # Test audit logging for rate limiting
        print("\n--- Testing rate limit audit logging ---")

        LOCK_ID = "lock_001"
        WRONG_LOCK_PASSWORD = "definitely_wrong_lock_password"

        # Reset only Alice's rate-limit state for this lock
        db.query(UnlockAttempt).filter(
            UnlockAttempt.username == USERNAME,
            UnlockAttempt.lock_id == LOCK_ID
        ).delete(synchronize_session=False)
        db.commit()

        # Save the latest audit log ID before the test
        latest_log = (
            db.query(AuditLog.id)
            .order_by(AuditLog.id.desc())
            .first()
        )
        previous_log_id = latest_log[0] if latest_log else 0

        # Send five requests with an incorrect lock password
        for attempt in range(1, 6):
            payload = {
                "lock_id": LOCK_ID,
                "lock_password": WRONG_LOCK_PASSWORD,
                "timestamp": int(time.time()),
                "nonce": secrets.token_urlsafe(16)
            }

            response = requests.post(
                f"{SERVER_URL}/lock/unlock",
                json=payload,
                headers=headers,
                verify=CERT_PATH,
                timeout=5
            )

            print(
                f"Failed attempt {attempt}: "
                f"HTTP {response.status_code}"
            )

            # The fifth failed attempt activates the rate limit
            expected_status = 429 if attempt == 5 else 401

            assert response.status_code == expected_status, (
                f"Attempt {attempt}: expected HTTP {expected_status}, "
                f"got {response.status_code}: {response.text}"
            )

        # Verify that reaching the threshold was logged
        threshold_log = (
            db.query(AuditLog)
            .filter(
                AuditLog.id > previous_log_id,
                AuditLog.username == USERNAME,
                AuditLog.event_type == "rate_limit",
                AuditLog.result == "blocked",
                AuditLog.reason == "maximum_failed_attempts_reached"
            )
            .order_by(AuditLog.id.desc())
            .first()
        )

        assert threshold_log is not None, (
            "Reaching the failed-attempt limit was not recorded"
        )

        print("PASS: Rate-limit threshold was recorded in AuditLog")
        print("Event:", threshold_log.event_type)
        print("Result:", threshold_log.result)
        print("Reason:", threshold_log.reason)

        # Send one more request while the user-lock pair is blocked
        blocked_payload = {
            "lock_id": LOCK_ID,
            "lock_password": "987654",
            "timestamp": int(time.time()),
            "nonce": secrets.token_urlsafe(16)
        }

        blocked_response = requests.post(
            f"{SERVER_URL}/lock/unlock",
            json=blocked_payload,
            headers=headers,
            verify=CERT_PATH,
            timeout=5
        )

        print(
            "Request while blocked:",
            blocked_response.status_code
        )

        assert blocked_response.status_code == 429, (
            "Expected HTTP 429 while rate-limited, "
            f"got {blocked_response.status_code}: "
            f"{blocked_response.text}"
        )

        # Verify that the blocked request was also recorded
        blocked_log = (
            db.query(AuditLog)
            .filter(
                AuditLog.id > previous_log_id,
                AuditLog.username == USERNAME,
                AuditLog.event_type == "rate_limit",
                AuditLog.result == "blocked",
                AuditLog.reason ==
                    "account_lock_pair_temporarily_blocked"
            )
            .order_by(AuditLog.id.desc())
            .first()
        )

        assert blocked_log is not None, (
            "Blocked request was not recorded in AuditLog"
        )

        print("PASS: Blocked request was recorded in AuditLog")
        print("Event:", blocked_log.event_type)
        print("Result:", blocked_log.result)
        print("Reason:", blocked_log.reason)
        print("IP address:", blocked_log.ip_address)

    finally:
        # Always close the database session
        db.close()


if __name__ == "__main__":
    main()
