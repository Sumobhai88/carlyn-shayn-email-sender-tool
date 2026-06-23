"""
Database session and engine configuration
Production-ready SQLAlchemy setup with FastAPI dependency injection

Best Practices:
- Connection pooling configuration
- Session lifecycle management
- Proper error handling
- Context managers for cleanup
- Type hints for IDE support
"""
from sqlalchemy import create_engine, event, pool, text
from sqlalchemy.orm import sessionmaker, Session, scoped_session
from sqlalchemy.engine import Engine
from typing import Generator
from contextlib import contextmanager
import logging

from app.core.config import settings

# Configure logging
logger = logging.getLogger(__name__)

# ==============================================================================
# ENGINE CONFIGURATION
# ==============================================================================

# SQLite specific configuration
sqlite_connect_args = {
    "check_same_thread": False,  # Allow multi-threading
    "timeout": 30.0,  # Connection timeout in seconds
    "isolation_level": None  # Autocommit mode for better concurrency
}

engine_kwargs = {
    "connect_args": sqlite_connect_args if "sqlite" in settings.DATABASE_URL else {},
    "poolclass": pool.StaticPool if "sqlite" in settings.DATABASE_URL else pool.QueuePool,
    "pool_pre_ping": True,
    "echo": settings.DEBUG,
    "echo_pool": False,
    "future": True,
}

if "sqlite" not in settings.DATABASE_URL:
    engine_kwargs.update({
        "pool_size": 5,
        "max_overflow": 10,
        "pool_timeout": 30,
        "pool_recycle": 3600,
    })

# Create SQLAlchemy engine with optimizations
engine = create_engine(settings.DATABASE_URL, **engine_kwargs)


# ==============================================================================
# SESSION CONFIGURATION
# ==============================================================================

# Create sessionmaker factory
SessionLocal = sessionmaker(
    autocommit=False,  # Manual transaction control
    autoflush=False,   # Don't auto-flush before queries
    bind=engine,
    expire_on_commit=False  # Keep objects usable after commit
)

# Thread-local session for background tasks (optional)
ScopedSession = scoped_session(SessionLocal)


# ==============================================================================
# SQLITE OPTIMIZATIONS
# ==============================================================================

@event.listens_for(Engine, "connect")
def set_sqlite_pragma(dbapi_conn, connection_record):
    """
    Configure SQLite for optimal performance
    Runs on every new connection
    """
    if "sqlite" in str(dbapi_conn):
        cursor = dbapi_conn.cursor()
        # Enable foreign key support
        cursor.execute("PRAGMA foreign_keys=ON")
        # Use Write-Ahead Logging for better concurrency
        cursor.execute("PRAGMA journal_mode=WAL")
        # Synchronous mode for safety vs speed balance
        cursor.execute("PRAGMA synchronous=NORMAL")
        # Cache size (negative = KB, positive = pages)
        cursor.execute("PRAGMA cache_size=-64000")  # 64MB cache
        # Temp storage in memory
        cursor.execute("PRAGMA temp_store=MEMORY")
        # Memory-mapped I/O
        cursor.execute("PRAGMA mmap_size=268435456")  # 256MB
        cursor.close()
        logger.debug("SQLite pragmas configured for connection")


# ==============================================================================
# DEPENDENCY INJECTION
# ==============================================================================

def get_db() -> Generator[Session, None, None]:
    """
    FastAPI dependency for database session
    
    Usage:
        @app.get("/users")
        def get_users(db: Session = Depends(get_db)):
            return db.query(User).all()
    
    Features:
        - Automatic session creation
        - Exception handling
        - Guaranteed cleanup
        - Type hints for IDE support
    """
    db = SessionLocal()
    try:
        yield db
    except Exception as e:
        logger.error(f"Database session error: {str(e)}")
        db.rollback()
        raise
    finally:
        db.close()


# ==============================================================================
# CONTEXT MANAGERS
# ==============================================================================

@contextmanager
def get_db_context():
    """
    Context manager for database session
    
    Usage:
        with get_db_context() as db:
            user = db.query(User).first()
    
    Use this for background tasks or scripts
    """
    db = SessionLocal()
    try:
        yield db
        db.commit()
    except Exception as e:
        logger.error(f"Database transaction error: {str(e)}")
        db.rollback()
        raise
    finally:
        db.close()


# ==============================================================================
# HELPER FUNCTIONS
# ==============================================================================

def init_db():
    """
    Initialize database - create all tables
    Call this on application startup
    """
    from app.db.base import Base
    
    logger.info("Creating database tables...")
    Base.metadata.create_all(bind=engine)
    logger.info("✓ Database tables created successfully")


def drop_db():
    """
    Drop all tables - USE WITH CAUTION!
    Only for testing/development
    """
    from app.db.base import Base
    
    if not settings.DEBUG:
        raise RuntimeError("Cannot drop database in production mode")
    
    logger.warning("Dropping all database tables...")
    Base.metadata.drop_all(bind=engine)
    logger.info("✓ All tables dropped")


def reset_db():
    """
    Reset database - drop and recreate all tables
    Only for development/testing
    """
    if not settings.DEBUG:
        raise RuntimeError("Cannot reset database in production mode")
    
    drop_db()
    init_db()
    logger.info("✓ Database reset complete")


def check_db_connection():
    """
    Check database connectivity
    Returns True if connection is successful
    """
    try:
        with engine.connect() as conn:
            conn.execute(text("SELECT 1"))
        logger.info("✓ Database connection successful")
        return True
    except Exception as e:
        logger.error(f"✗ Database connection failed: {str(e)}")
        return False


def get_db_info():
    """
    Get database information for diagnostics
    """
    info = {
        "url": str(engine.url),
        "driver": engine.driver,
        "dialect": engine.dialect.name,
        "pool_size": engine.pool.size() if hasattr(engine.pool, 'size') else None,
        "checked_out": engine.pool.checkedout() if hasattr(engine.pool, 'checkedout') else 0,
    }
    return info


# ==============================================================================
# SHUTDOWN HANDLER
# ==============================================================================

def close_db():
    """
    Close all database connections
    Call this on application shutdown
    """
    logger.info("Closing database connections...")
    engine.dispose()
    logger.info("✓ Database connections closed")


# ==============================================================================
# TRANSACTION DECORATORS (Optional)
# ==============================================================================

def transactional(func):
    """
    Decorator for automatic transaction management
    
    Usage:
        @transactional
        def create_user(db: Session, user_data: dict):
            user = User(**user_data)
            db.add(user)
            return user
    """
    from functools import wraps
    
    @wraps(func)
    def wrapper(*args, **kwargs):
        # Find db session in args or kwargs
        db = kwargs.get('db') or (args[0] if args and isinstance(args[0], Session) else None)
        
        if not db:
            raise ValueError("No database session found in function arguments")
        
        try:
            result = func(*args, **kwargs)
            db.commit()
            return result
        except Exception as e:
            db.rollback()
            logger.error(f"Transaction failed: {str(e)}")
            raise
    
    return wrapper


# ==============================================================================
# EXPORTS
# ==============================================================================

__all__ = [
    "engine",
    "SessionLocal",
    "ScopedSession",
    "get_db",
    "get_db_context",
    "init_db",
    "drop_db",
    "reset_db",
    "check_db_connection",
    "get_db_info",
    "close_db",
    "transactional"
]
