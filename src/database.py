from pathlib import Path
from sqlalchemy import create_engine, event
from sqlalchemy.engine import URL
from sqlalchemy.orm import declarative_base, sessionmaker


BASE_DIR = Path(__file__).resolve().parent
DATABASE_PATH = BASE_DIR / "database.db"

DATABASE_URL = URL.create(
    drivername="sqlite",
    database=str(DATABASE_PATH)
)

# database & sqlalchemy connector
engine = create_engine(
    DATABASE_URL,
    connect_args={"check_same_thread": False}
)

# Enable foreign key enforcement for every SQLite connection.
@event.listens_for(engine, "connect")
def enable_foreign_keys(dbapi_connection, connection_record):

    cursor = dbapi_connection.cursor()

    cursor.execute("PRAGMA foreign_keys=ON")

    cursor.close()


SessionLocal = sessionmaker(
    autocommit=False,
    autoflush=False,
    bind=engine
)

Base = declarative_base()


# for dependency injection
def get_db():
    db = SessionLocal()

    try:
        yield db
    finally:
        db.close()
