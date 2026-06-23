"""
Main FastAPI application entry point
Production-ready setup with proper lifecycle management
"""
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.middleware.gzip import GZipMiddleware
from fastapi.middleware.trustedhost import TrustedHostMiddleware
from contextlib import asynccontextmanager
import logging

from app.core.config import settings
from app.api.v1.router import api_router
from app.db.database import init_db, close_db, check_db_connection, get_db_info
from app.services.campaign_engine import campaign_engine

# Configure logging
logging.basicConfig(
    level=logging.INFO if not settings.DEBUG else logging.DEBUG,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


# ==============================================================================
# LIFESPAN CONTEXT MANAGER
# ==============================================================================

@asynccontextmanager
async def lifespan(app: FastAPI):
    """
    Application lifespan handler
    Manages startup and shutdown events
    """
    # Startup
    logger.info("=" * 70)
    logger.info(f"🚀 Starting {settings.APP_NAME} v{settings.APP_VERSION}")
    logger.info("=" * 70)
    
    # Initialize database
    try:
        logger.info("📊 Initializing database...")
        init_db()
        
        # Check connection
        if check_db_connection():
            logger.info("✓ Database connection verified")
            
            # Log database info
            db_info = get_db_info()
            logger.info(f"✓ Database: {db_info['dialect']}")
            logger.info(f"✓ Driver: {db_info['driver']}")
        else:
            logger.error("✗ Database connection failed!")
            
    except Exception as e:
        logger.error(f"✗ Database initialization failed: {str(e)}")
        raise
    
    logger.info("=" * 70)
    logger.info(f"✓ Application started successfully")
    logger.info(f"📚 API Docs: http://{settings.HOST}:{settings.PORT}/api/docs")
    logger.info("=" * 70)
    
    yield  # Application runs here
    
    # Shutdown
    logger.info("=" * 70)
    logger.info("🛑 Shutting down application...")
    logger.info("=" * 70)

    # Stop all background email sending threads
    try:
        campaign_engine.stop_all()
        logger.info("✓ All campaign threads stopped")
    except Exception as e:
        logger.error(f"✗ Error stopping campaign threads: {str(e)}")

    # Close database connections
    try:
        close_db()
        logger.info("✓ Database connections closed")
    except Exception as e:
        logger.error(f"✗ Error closing database: {str(e)}")
    
    logger.info("=" * 70)
    logger.info("✓ Application shutdown complete")
    logger.info("=" * 70)


# ==============================================================================
# APPLICATION SETUP
# ==============================================================================

app = FastAPI(
    title=settings.APP_NAME,
    version=settings.APP_VERSION,
    description="Premium Email Automation Platform API - Production Ready",
    docs_url="/api/docs",
    redoc_url="/api/redoc",
    lifespan=lifespan,
    debug=settings.DEBUG,
    # Additional configurations
    openapi_url="/api/openapi.json",
    swagger_ui_parameters={
        "defaultModelsExpandDepth": -1,  # Hide schemas section by default
        "docExpansion": "list",  # Expand only tags
        "filter": True,  # Enable search
        "syntaxHighlight.theme": "monokai"  # Dark theme for code
    }
)


# ==============================================================================
# MIDDLEWARE CONFIGURATION
# ==============================================================================

# CORS Middleware - Configure cross-origin requests
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.ALLOWED_ORIGINS,
    allow_credentials=True,
    allow_methods=["GET", "POST", "PUT", "DELETE", "OPTIONS", "PATCH"],
    allow_headers=["*"],
    expose_headers=["X-Total-Count", "X-Page-Count"],
    max_age=3600  # Cache preflight requests for 1 hour
)

# GZip Middleware - Compress responses
app.add_middleware(
    GZipMiddleware, 
    minimum_size=1000,  # Only compress responses > 1KB
    compresslevel=5  # Balance between speed and compression
)

# Trusted Host Middleware - Prevent Host header attacks
if not settings.DEBUG:
    app.add_middleware(
        TrustedHostMiddleware,
        allowed_hosts=["*.carlyshayn.com", "localhost", "127.0.0.1"]
    )


# ==============================================================================
# ROUTERS
# ==============================================================================

# Include API router
app.include_router(api_router, prefix="/api/v1")


# ==============================================================================
# ROOT ENDPOINTS
# ==============================================================================

@app.get("/", tags=["Root"])
async def root():
    """
    Root endpoint - API information
    """
    return {
        "message": "Carlyn Shayn Email Engine API",
        "version": settings.APP_VERSION,
        "status": "operational",
        "docs": "/api/docs",
        "redoc": "/api/redoc",
        "openapi": "/api/openapi.json"
    }


@app.get("/health", tags=["Health"])
async def health_check():
    """
    Health check endpoint for monitoring
    Used by load balancers and monitoring systems
    """
    # Check database connection
    db_healthy = check_db_connection()
    
    return {
        "status": "healthy" if db_healthy else "unhealthy",
        "version": settings.APP_VERSION,
        "database": "connected" if db_healthy else "disconnected",
        "debug_mode": settings.DEBUG
    }


@app.get("/api/info", tags=["Info"])
async def api_info():
    """
    API information and statistics
    """
    db_info = get_db_info()
    
    return {
        "app_name": settings.APP_NAME,
        "version": settings.APP_VERSION,
        "environment": "development" if settings.DEBUG else "production",
        "database": {
            "dialect": db_info["dialect"],
            "driver": db_info["driver"],
            "pool_size": db_info["pool_size"],
            "connections_in_use": db_info["checked_out"]
        },
        "features": {
            "smtp_profiles": True,
            "campaigns": True,
            "analytics": True,
            "exports": True,
            "templates": True
        }
    }


# ==============================================================================
# ERROR HANDLERS (Optional - for custom error pages)
# ==============================================================================

@app.exception_handler(404)
async def not_found_handler(request, exc):
    """Custom 404 handler"""
    return {
        "error": "Not Found",
        "message": "The requested resource was not found",
        "path": str(request.url),
        "docs": "/api/docs"
    }


@app.exception_handler(500)
async def internal_error_handler(request, exc):
    """Custom 500 handler"""
    logger.error(f"Internal server error: {str(exc)}")
    return {
        "error": "Internal Server Error",
        "message": "An unexpected error occurred",
        "support": "contact@carlyshayn.com"
    }


# ==============================================================================
# DEVELOPMENT SERVER
# ==============================================================================

if __name__ == "__main__":
    import uvicorn
    
    logger.info(f"Starting development server...")
    logger.info(f"Environment: {'Development' if settings.DEBUG else 'Production'}")
    
    uvicorn.run(
        "app.main:app",
        host=settings.HOST,
        port=settings.PORT,
        reload=settings.DEBUG,
        log_level="debug" if settings.DEBUG else "info",
        access_log=True,
        use_colors=True
    )
