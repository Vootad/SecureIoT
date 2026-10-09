# Week 3 — Lock Simulator

## Objective

The goal of Week 3 is to implement a Python-based Smart Lock Simulator
and connect it to the FastAPI authentication server.

The Lock Simulator represents the IoT smart lock in the system.

## System Flow

The basic communication flow is:

Smart Lock Simulator
        |
        | HTTP Request
        v
FastAPI Server
        |
        v
Authentication
        |
        v
SQLite Database
        |
        v
Allow / Deny
        |
        v
Smart Lock Simulator

## Lock Simulator Responsibilities

The Lock Simulator is responsible for:

- Receiving the unlock code from the user
- Sending requests to the authentication server
- Receiving the server response
- Displaying the access result

## Authentication Flow

The `/lock/unlock` endpoint requires an authenticated user.

Therefore, the Lock Simulator will first authenticate with the server
and obtain an authentication token.

The token will then be included in the unlock request.

The unlock request contains:

- Lock ID
- Lock unlock code
- Authentication token

## Current Implementation

The Lock Simulator is implemented as a Python program.

At this stage, the client is being developed locally and communicates
with the FastAPI server through HTTP.

Security mechanisms such as HTTPS/TLS and protection against replay
attacks will be implemented in later stages of the project.

## Client-Server Authentication

The Smart Lock Simulator communicates with the FastAPI server through
HTTP requests.

Before sending an unlock request, the client authenticates the user
through the `/auth/login` endpoint.

If the credentials are valid, the server generates an access token.
The client stores this token temporarily and uses it in the
Authorization header of the unlock request.

The authentication flow is:

1. The Smart Lock Simulator receives the username and password.
2. The client sends a POST request to `/auth/login`.
3. The server verifies the user's credentials.
4. The server generates an access token.
5. The client receives the access token.
6. The client sends the unlock request with the access token.

## Unlock Request

The Smart Lock Simulator sends a POST request to:

`/lock/unlock`

The request contains:

- `lock_id`
- `lock_password`

The authentication token is sent through the HTTP Authorization header:

`Authorization: Bearer <access_token>`

The server then:

1. Validates the authentication token.
2. Identifies the authenticated user.
3. Searches for the requested lock.
4. Verifies the lock password.
5. Grants or denies access.

## Current Client-Server Flow

Smart Lock Simulator
        |
        | POST /auth/login
        v
FastAPI Authentication
        |
        | Access Token
        v
Smart Lock Simulator
        |
        | POST /lock/unlock
        | Authorization: Bearer Token
        | lock_id + lock_password
        v
FastAPI
        |
        v
Authentication + Lock Verification
        |
        +----> Access Granted
        |
        +----> Access Denied


## Testing

The Lock Simulator was tested against several functional and error
scenarios.

| Test Case | Input / Condition | Expected Result |
|---|---|---|
| Successful Login | Valid username and password | Authentication successful |
| Failed Login | Invalid username or password | Login rejected |
| Successful Unlock | Valid user and valid lock credentials | Access granted |
| Failed Unlock | Valid user and invalid lock credentials | Access denied |
| Server Unavailable | FastAPI server is offline | Connection error is displayed |

The client also uses a five-second request timeout to prevent waiting
indefinitely for a server response.

Network-related request errors are handled by the Lock Simulator
without terminating the application with an unhandled exception.

## Core Test Cases

The following test cases were performed to verify the main functionality
of the Smart Lock Simulator and Authentication Server.

| Test Case           | Input / Condition                     | Expected Result                                           | Status |
| ------------------- | ------------------------------------- | --------------------------------------------------------- | ------ |
| Server Available    | FastAPI server is running             | Simulator starts authentication                           | Passed |
| Server Unavailable  | FastAPI server is offline             | Simulator detects the unavailable server and stops        | Passed |
| Valid Login         | Correct username and password         | Authentication succeeds and an access token is returned   | Passed |
| Invalid Login       | Incorrect username or password        | Authentication fails and unlock process does not continue | Passed |
| Valid Unlock        | Valid token, lock ID, and unlock code | Access is granted                                         | Passed |
| Invalid Unlock Code | Valid token and incorrect unlock code | Access is denied                                          | Passed |
| Invalid Lock ID     | Valid token and unknown lock ID       | Access is denied                                          | Passed |
