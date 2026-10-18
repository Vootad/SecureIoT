# Week 6: Security Logging and Testing

## 1. Overview

The goal of Week 6 was to improve the observability of the SecureIoT access control system by implementing security audit logging and verifying important security controls through automated tests.

The work focused on recording security-related events, testing the behavior of replay prevention and rate limiting, and verifying HTTPS communication.

## 2. Security Audit Logging

An audit logging mechanism was implemented to record important security events in the system.

The audit log records the following fields:

- **Timestamp:** The time when the event was recorded.
- **Username:** The user associated with the event, when available.
- **IP Address:** The client IP address associated with the request, when available.
- **Event Type:** The category of the event.
- **Result:** The outcome of the event.
- **Reason:** Additional information explaining the outcome.

Audit records are stored in the SQLite database using the `AuditLog` model.

### Logged Events

The implemented logging covers the following events:

- Successful authentication.
- Failed authentication.
- Unlock requests and denied unlock attempts.
- Replay attack detection.
- Rate-limit activation.
- Requests rejected while a user-lock pair is temporarily blocked.

These records help with troubleshooting and reviewing security-related activity.

## 3. Security Testing

Automated tests were used to verify the audit logging behavior and selected security controls.

### 3.1 Authentication Logging

The tests verified that successful and failed login attempts were recorded with the expected event types, results, and reasons.

### 3.2 Unlock Failure Logging

An unlock request with an incorrect lock password was rejected and recorded in the audit log.

### 3.3 Replay Attack Logging

The same unlock request was submitted twice using the same nonce. The first request succeeded, while the repeated request was rejected with HTTP 409 Conflict and recorded as a replay attempt.

### 3.4 Rate-Limiting Logging

Repeated incorrect unlock attempts triggered the configured rate limit. The test verified that the threshold event was recorded and that a subsequent request during the blocking period was rejected with HTTP 429 Too Many Requests.

The audit log recorded the reasons `maximum_failed_attempts_reached` and `account_lock_pair_temporarily_blocked`.

## 4. TLS/HTTPS Verification

A separate test script, `test_tls.py`, was added to verify HTTPS behavior.

The test confirmed that:

- An HTTPS request to the health endpoint succeeded with HTTP 200 when the server certificate was verified using the local certificate file.
- A plain HTTP request to the HTTPS server port was rejected.

These tests verify the expected behavior in the local development environment. They do not constitute a complete security assessment of the TLS configuration.

## 5. Test Results

All tests executed during this stage passed in the local development environment.

| Test | Result |
|---|---|
| Failed login audit logging | Passed |
| Successful login audit logging | Passed |
| Invalid lock password audit logging | Passed |
| Replay attempt detection and logging | Passed |
| Rate-limit threshold logging | Passed |
| Logging requests during a blocking period | Passed |
| HTTPS certificate verification | Passed |
| HTTP request to the HTTPS port | Rejected as expected |

## 6. Conclusion

Week 6 improved the observability and test coverage of the SecureIoT access control system.

Security-related events can now be reviewed through audit records in the database. Automated tests also verified the expected behavior of authentication logging, unlock denial, replay prevention, rate limiting, and local HTTPS communication.

The system is still a development prototype. Additional work would be required before production deployment, including a broader security assessment, secure certificate and key management, and appropriate protection and retention policies for audit logs.