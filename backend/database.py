from sqlalchemy import create_engine, event
from sqlalchemy.orm import declarative_base, sessionmaker
from sqlalchemy.pool import StaticPool
import os
import logging

logger = logging.getLogger(__name__)

DATABASE_URL = os.getenv("DATABASE_URL", "sqlite:///./biocopilot.db")

# Security: Configure connection pooling and SQL Alchemy security settings
if DATABASE_URL.startswith("sqlite"):
    connect_args = {"check_same_thread": False}
    engine = create_engine(
        DATABASE_URL,
        connect_args=connect_args,
        poolclass=StaticPool,
        echo=os.getenv("ENVIRONMENT") == "development",
    )
    # Enable foreign keys for SQLite
    @event.listens_for(engine, "connect")
    def set_sqlite_pragma(dbapi_conn, connection_record):
        cursor = dbapi_conn.cursor()
        cursor.execute("PRAGMA foreign_keys=ON")
        cursor.close()
else:
    # For production databases (PostgreSQL, MySQL, etc.)
    engine = create_engine(
        DATABASE_URL,
        pool_size=10,
        max_overflow=20,
        pool_pre_ping=True,  # Test connections before using
        echo=False,
    )

SessionLocal = sessionmaker(bind=engine, autoflush=False, autocommit=False, expire_on_commit=True)
Base = declarative_base()

def get_db():
    """Get database session with proper cleanup."""
    db = SessionLocal()
    try:
        yield db
    except Exception as e:
        logger.error(f"Database error: {type(e).__name__}")
        db.rollback()
        raise
    finally:
        db.close()
