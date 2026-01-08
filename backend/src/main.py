"""
ActionMind AI - FastAPI Backend Application
Main entry point for the API server
"""

from contextlib import asynccontextmanager
from fastapi import FastAPI, Request, status, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from fastapi.exceptions import RequestValidationError
import uvicorn
import logging

from src.core.config import settings
from src.core.database import engine, Base
from src.api import auth, tasks

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Lifespan context manager for startup and shutdown events"""
    # Startup: Create database tables
    logger.info("Creating database tables...")
    Base.metadata.create_all(bind=engine)
    logger.info(f"CORS allowed origins: {settings.cors_origins_list}")
    yield
    # Shutdown: Close database connections
    logger.info("Closing database connections...")
    engine.dispose()


# Create FastAPI application
app = FastAPI(
    title="ActionMind AI API",
    description="Task Management API with JWT Authentication",
    version="1.0.0",
    lifespan=lifespan,
)

# Configure CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.cors_origins_list,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


def get_cors_headers(origin: str | None) -> dict:
    """Get CORS headers for the given origin"""
    if not origin:
        return {}

    allowed_origins = settings.cors_origins_list
    if origin in allowed_origins:
        return {
            "Access-Control-Allow-Origin": origin,
            "Access-Control-Allow-Credentials": "true",
        }
    elif "*" in allowed_origins:
        return {
            "Access-Control-Allow-Origin": "*",
        }
    return {}


# HTTPException handler to ensure CORS headers on 4xx/5xx errors
@app.exception_handler(HTTPException)
async def http_exception_handler(request: Request, exc: HTTPException):
    """Handle HTTPException and ensure CORS headers are present"""
    cors_headers = get_cors_headers(request.headers.get("origin"))

    return JSONResponse(
        status_code=exc.status_code,
        content={"detail": exc.detail},
        headers=cors_headers
    )


# Validation error handler to ensure CORS headers on 422 errors
@app.exception_handler(RequestValidationError)
async def validation_exception_handler(request: Request, exc: RequestValidationError):
    """Handle validation errors and ensure CORS headers are present"""
    cors_headers = get_cors_headers(request.headers.get("origin"))

    return JSONResponse(
        status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
        content={"detail": exc.errors()},
        headers=cors_headers
    )


# Global exception handler for unhandled exceptions
@app.exception_handler(Exception)
async def global_exception_handler(request: Request, exc: Exception):
    """Handle all exceptions and ensure CORS headers are present"""
    cors_headers = get_cors_headers(request.headers.get("origin"))
    logger.error(f"Unhandled exception: {exc}", exc_info=True)

    return JSONResponse(
        status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
        content={"detail": str(exc)},
        headers=cors_headers
    )


# Include routers
app.include_router(auth.router, prefix=settings.API_PREFIX, tags=["auth"])
app.include_router(tasks.router, prefix=settings.API_PREFIX, tags=["tasks"])


@app.get("/")
async def root():
    """Root endpoint"""
    return {
        "message": "ActionMind AI API",
        "version": "1.0.0",
        "docs": "/docs",
    }


@app.get("/health")
async def health_check():
    """Health check endpoint"""
    return {"status": "healthy"}


if __name__ == "__main__":
    uvicorn.run(
        "src.main:app",
        host=settings.API_HOST,
        port=settings.API_PORT,
        reload=settings.DEBUG,
    )
