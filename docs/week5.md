# Week 5 – Security Controls

## 1. Replay Attack Prevention

Replay attack prevention was implemented to prevent previously captured unlock requests from being reused.

Each unlock request contains:
- **Timestamp:** The server rejects requests that are more than 30 seconds old or too far in the future.
- **Nonce:** A unique random value is generated for each request.
- **Server-side validation:** The server checks whether the nonce has already been used.

After a valid unlock request passes credential verification, its nonce is stored in the database. If the same nonce is submitted again, the server rejects the request with HTTP 409.

**Expected behavior:** The first valid request succeeds, while a repeated request using the same nonce is rejected.

## 2. Rate Limiting

Rate limiting was implemented to reduce repeated attempts to guess a lock credential.

The mechanism uses the authenticated username and lock ID to track failed attempts independently.

Configuration:
- Maximum failed attempts: 5
- Temporary block duration: 60 seconds
- HTTP 401: Invalid lock credentials before reaching the limit
- HTTP 429: Too many failed attempts or a request made during an active block

After a successful unlock, the failed-attempt counter is reset. Once the temporary block expires, the counter is also reset when the next request is processed.

## 3. Testing

The following scenarios were tested:

| Test scenario | Expected result | Observed result |
|---|---|---|
| Four incorrect lock passwords | HTTP 401 | Passed |
| Fifth incorrect lock password | HTTP 429 | Passed |
| Correct password while blocked | HTTP 429 | Passed |
| Bob accesses the same lock while Alice is blocked | HTTP 200 | Passed |
| Reuse of an already-used nonce | HTTP 409 | Passed |

## 4. Summary

During Week 5, two security controls were added to the SecureIoT access-control system: replay attack prevention and rate limiting.

These mechanisms complement the existing authentication, password hashing, and TLS communication features by helping prevent repeated-request attacks and repeated credential-guessing attempts.