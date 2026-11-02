
import sqlite3
from pathlib import Path


# Find the directory containing this script.
BASE_DIR = Path(__file__).resolve().parent

# Define the database and backup paths.
DATABASE_PATH = BASE_DIR / "database.db"
BACKUP_PATH = BASE_DIR / "database_before_schema_migration.db"


def get_columns(cursor, table_name):
    """Return the column names of a database table."""

    return {
        row["name"]
        for row in cursor.execute(
            f'PRAGMA table_info("{table_name}")'
        ).fetchall()
    }


def run_migration():

    # Stop if the backup does not exist.
    if not BACKUP_PATH.exists():
        raise FileNotFoundError(
            f"Database backup not found: {BACKUP_PATH}"
        )

    if not DATABASE_PATH.exists():
        raise FileNotFoundError(
            f"Database not found: {DATABASE_PATH}"
        )

    connection = sqlite3.connect(DATABASE_PATH)
    connection.row_factory = sqlite3.Row

    try:
        connection.execute("PRAGMA foreign_keys=ON")
        cursor = connection.cursor()

        # Check the audit log table before migration.
        audit_columns = get_columns(cursor, "audit_logs")

        audit_count = cursor.execute(
            "SELECT COUNT(*) FROM audit_logs"
        ).fetchone()[0]

        if audit_count > 0:
            required_hash_columns = {
                "previous_hash",
                "current_hash"
            }

            if not required_hash_columns.issubset(audit_columns):
                raise RuntimeError(
                    "Audit logs are not empty and hash columns do not exist."
                )

            incomplete_logs = cursor.execute("""
                SELECT COUNT(*)
                FROM audit_logs
                WHERE previous_hash IS NULL
                   OR current_hash IS NULL
            """).fetchone()[0]

            if incomplete_logs > 0:
                raise RuntimeError(
                    "Some audit logs do not have complete hashes."
                )

        # Start a transaction.
        connection.execute("BEGIN IMMEDIATE")

        print("Starting Day 1 database migration...")

        # Add is_active to users if it does not exist.
        user_columns = get_columns(cursor, "users")

        if "is_active" not in user_columns:
            cursor.execute("""
                ALTER TABLE users
                ADD COLUMN is_active INTEGER NOT NULL DEFAULT 1
            """)
            print("Added users.is_active")
        else:
            print("users.is_active already exists")

        # Add is_active to locks if it does not exist.
        lock_columns = get_columns(cursor, "locks")

        if "is_active" not in lock_columns:
            cursor.execute("""
                ALTER TABLE locks
                ADD COLUMN is_active INTEGER NOT NULL DEFAULT 1
            """)
            print("Added locks.is_active")
        else:
            print("locks.is_active already exists")

        # Create the user-lock permission table.
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS user_lock_permissions (
                id INTEGER PRIMARY KEY,
                user_id INTEGER NOT NULL,
                lock_id INTEGER NOT NULL,
                created_at DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,

                CONSTRAINT uq_user_lock_permission
                UNIQUE (user_id, lock_id),

                FOREIGN KEY (user_id)
                REFERENCES users(id) ON DELETE CASCADE,

                FOREIGN KEY (lock_id)
                REFERENCES locks(id) ON DELETE CASCADE
            )
        """)

        # Create indexes for faster permission lookups.
        cursor.execute("""
            CREATE INDEX IF NOT EXISTS
            ix_user_lock_permissions_user_id
            ON user_lock_permissions(user_id)
        """)

        cursor.execute("""
            CREATE INDEX IF NOT EXISTS
            ix_user_lock_permissions_lock_id
            ON user_lock_permissions(lock_id)
        """)

        print("Created user_lock_permissions table and indexes")

        # Add hash columns to audit_logs.
        audit_columns = get_columns(cursor, "audit_logs")

        if "previous_hash" not in audit_columns:
            cursor.execute("""
                ALTER TABLE audit_logs
                ADD COLUMN previous_hash VARCHAR(64)
            """)
            print("Added audit_logs.previous_hash")

        if "current_hash" not in audit_columns:
            cursor.execute("""
                ALTER TABLE audit_logs
                ADD COLUMN current_hash VARCHAR(64)
            """)
            print("Added audit_logs.current_hash")

        # Validate existing user roles.
        invalid_roles = cursor.execute("""
            SELECT id, username, role
            FROM users
            WHERE role NOT IN ('admin', 'user')
        """).fetchall()

        if invalid_roles:
            raise RuntimeError(
                f"Invalid user roles detected: {[dict(row) for row in invalid_roles]}"
            )

        print("Existing user roles are valid")

        # Check database foreign keys.
        foreign_key_errors = cursor.execute(
            "PRAGMA foreign_key_check"
        ).fetchall()

        if foreign_key_errors:
            raise RuntimeError(
                f"Foreign key errors detected: {foreign_key_errors}"
            )

        # Save all changes.
        connection.commit()

        print("\nMigration completed successfully.")

    except Exception:
        # Undo all changes if something goes wrong.
        connection.rollback()

        print("\nMigration failed. Changes were rolled back.")
        raise

    finally:
        connection.close()


if __name__ == "__main__":
    run_migration()
