from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, DeclarativeBase
from sqlalchemy.pool import NullPool

from core.config import settings
from core.logging_config import get_logger

logger = get_logger(__name__)


class Base(DeclarativeBase):
    pass


# Create engine with connection pooling appropriate for serverless (Neon)
engine = create_engine(
    settings.DATABASE_URL,
    poolclass=NullPool,  # Neon PostgreSQL: NullPool avoids stale connections on serverless
    echo=False,
    connect_args={"connect_timeout": 60},  # Allow up to 60s for Neon cold start
)

SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)


def get_db():
    """Dependency that yields a database session."""
    db = SessionLocal()
    try:
        yield db
    except Exception as e:
        logger.error(f"Database session error: {e}")
        db.rollback()
        raise
    finally:
        db.close()


def create_tables():
    """Create all tables defined in models."""
    from infrastructure.database import models  # noqa: F401 - ensures models are registered
    logger.info("Creating database tables...")
    Base.metadata.create_all(bind=engine)
    logger.info("Database tables created successfully.")
