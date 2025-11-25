from fastapi import FastAPI, Request, status
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from fastapi.exceptions import RequestValidationError
from sqlalchemy.exc import SQLAlchemyError
import time

from app.api import ideas, generate
from app.config import get_settings
from app.logging_config import setup_logging, get_logger
from app.database import engine

# Setup logging on startup
setup_logging()
logger = get_logger(__name__)
settings = get_settings()

app = FastAPI(
    title="Binko.ai",
    description="Project Idea Generator",
    version="1.0.0"
)

# CORS - Use settings for production control
origins = settings.cors_origins.split(",") if settings.cors_origins != "*" else ["*"]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# Request logging middleware
@app.middleware("http")
async def log_requests(request: Request, call_next):
    """Log all requests with timing."""
    start_time = time.time()
    
    logger.info(f"Request: {request.method} {request.url.path}")
    
    try:
        response = await call_next(request)
        process_time = time.time() - start_time
        logger.info(f"Completed: {request.method} {request.url.path} - {response.status_code} - {process_time:.3f}s")
        return response
    except Exception as e:
        process_time = time.time() - start_time
        logger.error(f"Error: {request.method} {request.url.path} - {str(e)} - {process_time:.3f}s")
        raise


# Global exception handlers
@app.exception_handler(SQLAlchemyError)
async def database_exception_handler(request: Request, exc: SQLAlchemyError):
    """Handle database errors."""
    logger.error(f"Database error on {request.url.path}: {str(exc)}")
    return JSONResponse(
        status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
        content={"detail": "Database error. Try again later."}
    )


@app.exception_handler(RequestValidationError)
async def validation_exception_handler(request: Request, exc: RequestValidationError):
    """Handle validation errors."""
    logger.warning(f"Validation error on {request.url.path}: {exc.errors()}")
    return JSONResponse(
        status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
        content={"detail": exc.errors()}
    )


@app.exception_handler(Exception)
async def general_exception_handler(request: Request, exc: Exception):
    """Catch-all for unexpected errors."""
    logger.error(f"Unexpected error on {request.url.path}: {str(exc)}", exc_info=True)
    return JSONResponse(
        status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
        content={"detail": "Internal server error"}
    )


# Startup/shutdown events
@app.on_event("startup")
async def startup_event():
    """Log startup."""
    logger.info(f"Starting Binko.ai API - Environment: {settings.environment}")
    logger.info(f"CORS origins: {origins}")


@app.on_event("shutdown")
async def shutdown_event():
    """Cleanup on shutdown."""
    logger.info("Shutting down Binko.ai API")
    engine.dispose()


# Routes
app.include_router(ideas.router, prefix="/api/ideas", tags=["ideas"])
app.include_router(generate.router, prefix="/api/generate", tags=["generate"])


@app.get("/")
def root():
    """Root endpoint."""
    return {"status": "ok", "service": "binko.ai", "version": "1.0.0"}


@app.get("/health")
def health_check():
    """Health check endpoint for monitoring."""
    try:
        # Test database connection
        with engine.connect() as conn:
            conn.execute("SELECT 1")
        
        return {
            "status": "healthy",
            "service": "binko.ai",
            "database": "connected",
            "environment": settings.environment
        }
    except Exception as e:
        logger.error(f"Health check failed: {str(e)}")
        return JSONResponse(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            content={
                "status": "unhealthy",
                "service": "binko.ai",
                "database": "disconnected",
                "error": str(e)
            }
        )
