from sqlalchemy import Column, Integer, String, DateTime
from database import Base
from datetime import datetime


class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    username = Column(String, unique=True, nullable=False, index=True)
    password_hash = Column(String, nullable=False)
    role = Column(String, nullable=False)
    created_at = Column(DateTime)


class Lock(Base):
    __tablename__ = "locks"

    id = Column(Integer, primary_key=True, index=True)
    lock_id = Column(String, unique=True, nullable=False, index=True)
    password_hash = Column(String, nullable=False)
    created_at = Column(DateTime)


class UsedNonce(Base):
    __tablename__ = "used_nonce"

    id = Column(Integer, primary_key=True, index=True)
    nonce = Column(String, unique=True, nullable=False, index=True)
    created_at = Column(DateTime, default=datetime.utcnow)


class UnlockAttempt(Base):
    __tablename__ = "unlock_attempts"

    id = Column(Integer, primary_key=True, index=True)
    # Username of the authenticated user
    username = Column(String, nullable=False, index=True)
    lock_id = Column(String, nullable=False, index=True)
    failed_attempts = Column(Integer, default=0)
    blocked_until = Column(DateTime, nullable=True)


class LoginAttempt(Base):
    __tablename__ = "login_attempts"

    username = Column(String, nullable=False, index=True)
    id = Column(Integer, primary_key=True, index=True)
    ip = Column(String, nullable=False, index=True)
    failed_attempts = Column(Integer, default=0)
    blocked_until = Column(DateTime, nullable=True)


class AuditLog(Base):
    __tablename__ = "audit_logs"

    id = Column(Integer, primary_key=True, index=True)
    # Time when the security event accurred
    timestamp = Column(DateTime, default=datetime.utcnow, nullable=False)
    # Username associated with the event
    username = Column(String, nullable=True, index=True)
    # Cient IP address
    ip_address = Column(String, nullable=True)
    # Type of security event e.g. login or unlock
    event_type = Column(String, nullable=False, index=True)
    # Outcome of the event, e.g. success or failure
    result = Column(String, nullable=False)
    # Reason for the outcome, without sensitive information
    reason = Column(String, nullable=True)
