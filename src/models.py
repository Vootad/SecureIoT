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
