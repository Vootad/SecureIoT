# Week 7: Security Assessment and Testing

## 1. Overview

The goal of Week 7 was to evaluate the main security controls implemented in the SecureIoT access control system and verify their expected behavior through test scripts.

The assessment focused on password hashing, replay prevention, rate limiting, security audit logging, and TLS/HTTPS communication.

The purpose of these tests was to verify that the implemented controls behave as expected in the local development environment. The results do not represent a complete security assessment or prove that the system is free from vulnerabilities.

## 2. Password Hashing Verification

The password hashing mechanism was tested to verify that passwords are hashed and that password verification distinguishes between correct and incorrect passwords.

The test was executed using `test_security.py`.

### Results

- A password hash was generated using the configured password hashing mechanism.
- Verification of the correct password returned `True`.
- Verification of an incorrect password returned `False`.

These results confirm that the tested password hashing and verification functions behaved as expected.

## 3. Replay Protection Verification

Replay protection was tested by submitting the same unlock request twice using the same nonce.

### Test Procedure

1. Authenticate as a valid user.
2. Submit an unlock request with a valid timestamp and nonce.
3. Submit the same request again using the same nonce.
4. Examine the HTTP responses.

### Results

- The first unlock request returned HTTP 200 OK.
- The repeated request returned HTTP 409 Conflict.
- The server responded with `Replay attack detected`.

The results confirm that the system rejected the repeated request in this test scenario.

## 4. Rate Limiting Verification

The rate-limiting mechanism was tested by submitting repeated unlock requests with an incorrect lock password.

The configured threshold is five failed attempts, with a blocking period of 60 seconds.

### Test Procedure

1. Authenticate as Alice.
2. Submit unlock requests using an incorrect lock password.
3. Observe the responses as the failure threshold is reached.
4. Attempt to unlock the lock using the correct password while the restriction is active.
5. Authenticate as Bob and test access independently.

### Results

- The first four incorrect unlock attempts returned HTTP 401 Unauthorized.
- The fifth failed attempt returned HTTP 429 Too Many Requests.
- A subsequent request using the correct lock password was also rejected with HTTP 429 while the restriction remained active.
- Bob was able to authenticate and unlock the lock while Alice's account-lock pair was blocked.

These results confirm that the tested rate-limiting mechanism enforced the configured threshold and did not block Bob because Alice's account-lock pair was restricted.

### 4.1 Login Rate Limiting Verification

Login rate limiting was implemented to restrict repeated failed authentication attempts. The restriction is tracked using the username and client IP address. The configured threshold is five failed attempts, and the blocking period is 60 seconds.

#### Test Procedure

1. Submit login requests using an incorrect password for an existing test account.
2. Observe the HTTP responses for the failed attempts.
3. Attempt to log in again while the restriction is active, using the correct password.
4. Examine the response returned by the server.

#### Results

- The first five incorrect login attempts returned HTTP 401 Unauthorized.
- A subsequent login attempt was rejected with HTTP 429 Too Many Requests while the restriction was active, even when the correct password was provided.
- The test completed successfully, confirming that the implemented login rate-limiting behavior matched the expected results in this test scenario.

## 5. Security Audit Logging Verification

The audit logging mechanism was tested to verify that selected security events were recorded in the SQLite database with the expected event types, results, and reasons.

### Results

| Event | Expected behavior | Observed result |
|---|---|---|
| Failed login | Record a failed authentication event | Passed |
| Successful login | Record a successful authentication event | Passed |
| Replay attempt | Record the repeated request as denied | Passed |
| Invalid lock password | Record the denied unlock request | Passed |
| Rate-limit threshold | Record the blocking event | Passed |
| Request during blocking period | Record the blocked request | Passed |

The tests also verified selected audit fields, including the event type, result, reason, and client IP address.

Examples of recorded reasons included:

- `invalid_password`
- `authentication_successful`
- `duplicate_nonce`
- `invalid_lock_password`
- `maximum_failed_attempts_reached`
- `account_lock_pair_temporarily_blocked`

The results confirm that the tested security events were recorded as expected.

## 6. TLS/HTTPS Verification

The TLS test was executed using `test_tls.py` against the local HTTPS server.

### Test Procedure

1. Send an HTTPS request to the health endpoint while verifying the server certificate using the local certificate file.
2. Send a plain HTTP request to the HTTPS server port.
3. Examine the results.

### Results

- The HTTPS request succeeded with HTTP 200 OK when certificate verification was enabled.
- The plain HTTP request was rejected by the HTTPS server.

These results confirm the expected behavior of HTTPS communication and HTTP rejection in the local test environment. They do not constitute a comprehensive assessment of TLS versions, cipher suites, certificate lifecycle management, or other TLS security properties.

## 7. Summary of Test Results

| Test | Result |
|---|---|
| Password hashing and verification | Passed |
| Replay protection | Passed |
| Unlock rate limiting | Passed |
| Login rate limiting | Passed |
| Failed login audit logging | Passed |
| Successful login audit logging | Passed |
| Invalid lock password audit logging | Passed |
| Replay attempt audit logging | Passed |
| Rate-limit audit logging | Passed |
| HTTPS certificate verification | Passed |
| HTTP request to the HTTPS port | Rejected as expected |

All listed test scripts completed with the expected results in the local development environment.

## 8. Limitations

The tests cover selected security controls and scenarios. They do not prove that the system is completely secure.

The following limitations should be considered:

- The tests do not cover every possible authentication, authorization, or input-validation failure.
- Replay protection was verified for the tested repeated-request scenario; broader concurrency and edge-case testing has not been established by these results.
- Rate limiting was verified for the tested account-lock pair and threshold, but its behavior under concurrent requests and distributed deployments has not been assessed.
Login rate limiting was verified for the tested username and client IP address. Expiration of the blocking period, counter reset after successful authentication, and behavior under concurrent requests have not been fully assessed.
- TLS testing confirmed certificate verification and rejection of plain HTTP requests, but did not comprehensively assess the TLS configuration.
- Audit logging was verified for selected events. Log integrity, access control, retention, and resistance to tampering require separate assessment.
- The system has been evaluated in a local development environment and has not undergone a comprehensive penetration test.

## 9. Conclusion

Week 7 verified the expected behavior of the main security controls implemented in the SecureIoT access control system.

The executed tests confirmed password verification, replay rejection, unlock rate limiting, login rate limiting, selected security audit events, and HTTPS communication in the local development environment.

Together with the implementation and documentation completed in previous weeks, these results provide evidence of the project's core security functionality.

The system remains a development prototype. Further security testing, configuration review, and deployment hardening would be necessary before considering production use.