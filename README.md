# Secure IoT Access Control System

A Python-based IoT access control project that simulates a smart lock communicating with a backend server. The project focuses on authentication, secure communication, replay prevention, rate limiting, and security audit logging.

## Architecture

The system consists of three main components:

- **Smart Lock Simulator:** Sends access requests to the server.
- **FastAPI Server:** Authenticates users and validates lock-unlocking requests.
- **SQLite Database:** Stores application data and security-related records.

**Communication flow:**

`Smart Lock Simulator → FastAPI Server → SQLite Database`

## Features

- Password hashing with bcrypt.
- Token-based authentication.
- HTTPS/TLS communication.
- Replay attack prevention using timestamps and nonces.
- Separate rate limits for login and unlock attempts.
- Security audit logging.
- Automated security tests.

## Technologies

Python 3.11, FastAPI, Uvicorn, SQLAlchemy, SQLite, Passlib, bcrypt, Python-JOSE, Requests, Cryptography, and Pytest.

## Project Structure

```text
SecureIoT/
├── certs/
├── Design/
├── docs/
├── src/
│   ├── main.py
│   ├── lock_simulator.py
│   ├── database.py
│   ├── models.py
│   ├── schemas.py
│   ├── config.py
│   ├── dependencies.py
│   ├── auth_token.py
│   └── test/
├── requirements.txt
└── README.md
```

## Installation

From the project root, activate the existing virtual environment and install dependencies:

```powershell
.\src\venv\Scripts\Activate.ps1
python -m pip install -r requirements.txt
```

## Running the Server

```powershell
cd src
python -m uvicorn main:app --reload --ssl-certfile ..\certs\server.crt --ssl-keyfile ..\certs\server.key
```

API documentation is available at:

`https://127.0.0.1:8000/docs`

The server requires the local TLS certificate and private key at the specified paths.

## API Endpoints

| Method | Endpoint | Purpose |
|---|---|---|
| GET | `/health` | Health check |
| POST | `/auth/login` | User authentication |
| POST | `/lock/unlock` | Lock-unlocking request |

## Testing

Run the tests from the `src` directory:

```powershell
python -m pytest test
```

The test suite covers authentication security, replay prevention, TLS, rate limiting, and audit logging. Test results should be verified against the current project version.

## Documentation and Future Work

Additional implementation reports are available in `docs/`. Architecture and UML diagrams, security documentation, and demonstration evidence will be included as they are completed.

Potential future improvements include Docker integration, expanded security testing, and integration with physical IoT hardware.

## Limitations

This is an educational simulation intended for local development. It is not a production-ready smart lock system and has not undergone a comprehensive independent security assessment.
