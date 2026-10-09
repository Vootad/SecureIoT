# Week 4 — Secure Communication

## 1. Introduction

In Week 4, secure communication was added between the Smart Lock Simulator and the FastAPI server.

The main goal was to protect the communication channel using HTTPS/TLS and to ensure that the Smart Lock verifies the server's certificate before establishing a trusted connection.

Password security was also reviewed to ensure that user and lock passwords are not stored in plaintext.

## 2. Communication Before Week 4

Before Week 4, the Smart Lock Simulator communicated with the FastAPI server using HTTP:

Smart Lock Simulator
        |
        | HTTP
        v
FastAPI Server

## 3. Communication After Week 4

After implementing secure communication, the Smart Lock Simulator communicates with the FastAPI server using HTTPS.

```text
Smart Lock Simulator
        |
        | HTTPS
        | TLS
        v
FastAPI Server
        |
        v
SQLite Database
```

HTTPS protects the communication channel between the Smart Lock and the Server.

The client also verifies the server certificate before trusting the TLS connection.

## 4. HTTP vs HTTPS

HTTP is a protocol used for communication between clients and servers. However, HTTP does not provide encryption for the transmitted data.

HTTPS is HTTP transported over TLS. It protects the communication channel by providing encryption and helping ensure that data is not modified during transmission.

In this project, HTTPS is used because sensitive information such as authentication credentials and unlock requests are transmitted between the Smart Lock and the Server.


## 5. TLS

TLS (Transport Layer Security) is used to secure communication between the Smart Lock and the FastAPI server.

In this project, TLS provides:

* Confidentiality: transmitted data is encrypted.
* Integrity: helps detect unauthorized modification of transmitted data.
* Server authentication: the client can verify the server's certificate.

The project does not implement cryptographic algorithms directly. TLS is handled by the HTTPS stack and the underlying libraries.


## 6. Server Certificate

A self-signed certificate was generated for the development environment.

The server uses:

- server.crt — Server certificate
- server.key — Server private key

The Smart Lock Simulator does not simply disable certificate verification.

Instead, the client explicitly specifies the trusted server certificate:

```python
CERT_PATH = Path(__file__).resolve().parent.parent / "certs" / "server.crt"
```

The certificate is then passed to the `requests` library:

```python
verify=CERT_PATH
```

This configuration is used for the health check, login request, and unlock request.

Therefore, the Smart Lock verifies the server certificate when communicating with the FastAPI server.

## 7. Smart Lock Client Changes

The Smart Lock Simulator was updated to communicate with the server using HTTPS.

The server URL was changed from:

```text
http://127.0.0.1:8000
```

to:

```text
https://127.0.0.1:8000
```

The client also loads the trusted server certificate and uses it for certificate verification.

Certificate verification is applied to:

1. Server health check
2. User authentication
3. Lock unlock request


## 8. Password Security

Passwords are not stored in plaintext in the database.

The project uses bcrypt through Passlib for password hashing.

The process is:

```text
Password
    |
    v
bcrypt
    |
    v
Password Hash
    |
    v
Database
```

During authentication, the entered password is verified against the stored hash:

```text
Entered Password
       |
       v
Verify against stored hash
       |
   ┌───┴───┐
   |       |
Valid    Invalid
   |       |
Allow     Deny
```

The original password cannot be retrieved from the stored hash.


## 9. Why Passwords Are Not Stored in Plaintext

Storing passwords in plaintext is insecure because anyone who gains access to the database could directly read the passwords.

Instead, the project stores password hashes.

Even if the database is compromised, an attacker does not immediately obtain the original plaintext passwords.

The same principle is applied to both user passwords and lock passwords.


## 10. Security Testing

### 10.1 Normal HTTPS Connection

The Smart Lock Simulator was configured with the correct server certificate.

Expected result:

```text
Checking server connection...
Server connection successful
```

The authentication and unlock flow then completed successfully.

### 10.2 Invalid Certificate Test

To verify certificate validation, a different certificate was generated and temporarily configured as the trusted certificate in the Smart Lock Simulator.

The client rejected the TLS connection.

Expected result:

```text
Checking server connection...
Unable to connect to the server
Please make sure the server is running
```

This test confirmed that the Smart Lock does not blindly trust an arbitrary server certificate.

After the test, the original server certificate was restored.


## 11. Conclusion

Week 4 added secure communication to the SecureIoT system.

The Smart Lock Simulator now communicates with the FastAPI server through HTTPS/TLS, and the server certificate is verified by the client.

Password security was also maintained through bcrypt password hashing, ensuring that passwords are not stored in plaintext.

The main security improvements completed in this week are:

* HTTPS/TLS communication
* Server certificate verification
* Secure authentication communication
* Secure unlock communication
* bcrypt password hashing
* Certificate validation testing
