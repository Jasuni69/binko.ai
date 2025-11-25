from sqlalchemy import create_engine, event
from sqlalchemy.orm import sessionmaker, declarative_base
from sqlalchemy.exc import SQLAlchemyError
from app.config import get_settings
from app.logging_config import get_logger

settings = get_settings()
logger = get_logger(__name__)

# Connection pooling settings for production
engine = create_engine(
    settings.database_url,
    pool_size=5,  # Max connections in pool
    max_overflow=10,  # Max overflow connections
    pool_pre_ping=True,  # Check connection health before using
    pool_recycle=3600,  # Recycle connections after 1 hour
    echo=False,  # Don't log SQL (use SQLAlchemy logger instead)
)

SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()


@event.listens_for(engine, "connect")
def receive_connect(dbapi_conn, connection_record):
    """Log database connections."""
    logger.info("Database connection established")


@event.listens_for(engine, "close")
def receive_close(dbapi_conn, connection_record):
    """Log database disconnections."""
    logger.info("Database connection closed")


def get_db():
    """Dependency for database sessions with error handling."""
    db = SessionLocal()
    try:
        yield db
    except SQLAlchemyError as e:
        logger.error(f"Database error: {str(e)}")
        db.rollback()
        raise
    finally:
        db.close()
