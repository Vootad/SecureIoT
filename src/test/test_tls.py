import requests
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parents[2]
CERT_PATH = PROJECT_ROOT / "certs" / "server.crt"

HTTPS_URL = "https://127.0.0.1:8000/health"
HTTP_URL = "http://127.0.0.1:8000/health"
# CERT_PATH = "../certs/server.crt"


def main():
    print("--- Testing HTTPS with certificate verification ---")

    # Verify the server certificate using our local certificate file
    try:
        response = requests.get(
            HTTPS_URL,
            verify=CERT_PATH,
            timeout=5
        )

        print("HTTPS status:", response.status_code)

        assert response.status_code == 200
        print("PASS: HTTPS connection succeeded with certificate verification")

    except requests.exceptions.SSLError as error:
        print("FAIL: TLS certificate verification failed")
        print(error)
        raise

    print("\n--- Testing HTTP against the HTTPS server ---")

    # HTTP should not work on a port configured for HTTPS only
    try:
        response = requests.get(HTTP_URL, timeout=5)

        print("HTTP status:", response.status_code)
        raise AssertionError(
            "HTTP unexpectedly received an HTTP response from the HTTPS port"
        )

    except requests.exceptions.ConnectionError:
        print("PASS: HTTP connection was rejected")

    except requests.exceptions.RequestException as error:
        print("HTTP request failed:", error)
        print("Check whether the failure is caused by a protocol mismatch.")


if __name__ == "__main__":
    main()
