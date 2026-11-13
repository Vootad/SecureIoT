from sqlalchemy import (
    Column,
    Integer,
    String,
    DateTime,
    ForeignKey,
    UniqueConstraint
)
from sqlalchemy.orm import relationship

from database import Base
from datetime import datetime


class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    username = Column(String, unique=True, nullable=False, index=True)
    password_hash = Column(String, nullable=False)

    role = Column(String, nullable=False)

    is_active = Column(Integer, nullable=False, default=1, server_default="1")

    created_at = Column(DateTime)

    # Connects the user to their assigned lock permissions.
    permissions = relationship(
        "UserLockPermission",
        back_populates="user",
        cascade="all, delete-orphan"
    )


class Lock(Base):
    __tablename__ = "locks"

    id = Column(Integer, primary_key=True, index=True)
    lock_id = Column(String, unique=True, nullable=False, index=True)
    password_hash = Column(String, nullable=False)

    is_active = Column(Integer, nullable=False, default=1, server_default="1")

    created_at = Column(DateTime)

    # Connects the lock to users who have permission to access it.
    permissions = relationship(
        "UserLockPermission",
        back_populates="lock",
        cascade="all, delete-orphan"
    )


class UserLockPermission(Base):
    __tablename__ = "user_lock_permissions"

    id = Column(Integer, primary_key=True, index=True)

    # References the primary key of the users table.
    user_id = Column(
        Integer,
        ForeignKey("users.id", ondelete="CASCADE"),
        nullable=False,
        index=True
    )

    # References the primary key of the locks table.
    lock_id = Column(
        Integer,
        ForeignKey("locks.id", ondelete="CASCADE"),
        nullable=False,
        index=True
    )

    created_at = Column(
        DateTime,
        default=datetime.utcnow,
        nullable=False
    )

    # Prevents duplicate permissions for the same user and lock.
    __table_args__ = (
        UniqueConstraint(
            "user_id",
            "lock_id",
            name="uq_user_lock_permission"
        ),
    )

    user = relationship(
        "User",
        back_populates="permissions"
    )

    lock = relationship(
        "Lock",
        back_populates="permissions"
    )


class UsedNonce(Base):
    __tablename__ = "used_nonce"

    id = Column(Integer, primary_key=True, index=True)
    nonce = Column(String, unique=True, nullable=False, index=True)
    created_at = Column(DateTime, default=datetime.utcnow)


class UnlockAttempt(Base):
    __tablename__ = "unlock_attempts"

    id = Column(Integer, primary_key=True, index=True)
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

    # Time when the security event occurred.
    timestamp = Column(DateTime, default=datetime.utcnow, nullable=False)
    username = Column(String, nullable=True, index=True)
    ip_address = Column(String, nullable=True)

    # Type of security event, e.g. login or unlock.
    event_type = Column(String, nullable=False, index=True)
    result = Column(String, nullable=False)
    reason = Column(String, nullable=True)
