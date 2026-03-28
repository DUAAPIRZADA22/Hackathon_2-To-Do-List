"""
FastAPI Application for Todo AI Chatbot (Phase III)

Main application entry point with CORS middleware, exception handlers,
health check endpoint, and structured logging.

This file maintains backward compatibility with Phase I/II while adding
Phase III features (MCP + OpenAI Agents SDK + Structured Logging).

Architecture Principles:
- Type-safe: Pydantic models for all requests/responses
- CORS-enabled: Frontend integration ready
- Structured logging: Request ID tracking for debugging
- Health checks: Database and service monitoring
"""

import os
import uuid
from contextlib import asynccontextmanager
from typing import Callable

import structlog
from fastapi import FastAPI, Request, Response, status
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from fastapi.exceptions import RequestValidationError
from starlette.exceptions import HTTPException as StarletteHTTPException

# Phase I/II imports (maintain backward compatibility)
try:
    from src.core.config import settings
    from src.core.database import engine, Base
    from src.api import auth, tasks
    PHASE_II_AVAILABLE = True
except ImportError:
    # Phase III standalone mode
    PHASE_II_AVAILABLE = False
    settings = None

# Phase III imports
try:
    from backend.src.api.models import (
        ErrorResponse,
        HealthResponse,
        create_error_response,
        create_validation_error_response,
        ErrorCode,
    )
    from backend.src.db.session import init_db, close_db, check_db_connection
    from backend.src.mcp.server import get_mcp_server
except ImportError:
    # Fallback to relative imports when running from backend directory
    from src.api.models import (
        ErrorResponse,
        HealthResponse,
        create_error_response,
        create_validation_error_response,
        ErrorCode,
    )
    from src.db.session import init_db, close_db, check_db_connection
    from src.mcp.server import get_mcp_server


# =====================================================
# Structured Logging Configuration
# =====================================================

def configure_logging() -> None:
    """
    Configure structured logging with structlog.

    Logging format:
    - timestamp: ISO format timestamp
    - level: Log level (INFO, ERROR, etc.)
    - request_id: Unique request identifier
    - event: Event description
    - **kwargs: Additional context
    """
    log_level = os.getenv("LOG_LEVEL", "INFO").upper()

    structlog.configure(
        processors=[
            structlog.stdlib.filter_by_level,
            structlog.stdlib.add_logger_name,
            structlog.stdlib.add_log_level,
            structlog.processors.TimeStamper(fmt="iso"),
            structlog.processors.StackInfoRenderer(),
            structlog.processors.format_exc_info,
            structlog.processors.UnicodeDecoder(),
            structlog.processors.JSONRenderer()
        ],
        context_class=dict,
        logger_factory=structlog.stdlib.LoggerFactory(),
        wrapper_class=structlog.stdlib.BoundLogger,
        cache_logger_on_first_use=True,
    )

    logger = structlog.get_logger()
    logger.info("Logging configured", level=log_level)


# =====================================================
# Application Lifecycle
# =====================================================

@asynccontextmanager
async def lifespan(app: FastAPI):
    """
    Application lifespan manager.

    Handles startup and shutdown events:
    - Startup: Initialize database, MCP server, logging
    - Shutdown: Close database connections
    """
    logger = structlog.get_logger()
    logger.info("Starting Todo AI Chatbot API")

    # Configure logging
    configure_logging()

    # Phase I/II database initialization (if available) - MUST run first
    # This creates the users table that Phase III models depend on
    if PHASE_II_AVAILABLE:
        try:
            logger.info("Creating Phase I/II database tables...")
            Base.metadata.create_all(bind=engine)
            logger.info("Phase I/II database initialized")
        except Exception as e:
            logger.error("Failed to initialize Phase I/II database", error=str(e))

    # Initialize database (Phase III) - runs AFTER Phase I/II
    try:
        await init_db()
        logger.info("Phase III database initialized")
    except Exception as e:
        logger.error("Failed to initialize Phase III database", error=str(e))
        # Continue anyway - might be using Phase I/II database

    # Initialize MCP server with tools
    try:
        from backend.src.mcp.server import init_mcp_server_with_user_story_1
    except ImportError:
        from src.mcp.server import init_mcp_server_with_user_story_1

    try:
        mcp_server = init_mcp_server_with_user_story_1()
        logger.info(
            "MCP server initialized",
            tool_count=len(mcp_server.list_tools()),
            tools=mcp_server.list_tools()
        )
    except Exception as e:
        logger.error("Failed to initialize MCP server", error=str(e))
        # Continue anyway - tools will be unavailable

    # Check database connection
    db_connected = await check_db_connection()
    if not db_connected:
        logger.warning("Database connection check failed")

    yield

    # Shutdown
    logger.info("Shutting down Todo AI Chatbot API")
    await close_db()

    # Phase I/II cleanup
    if PHASE_II_AVAILABLE:
        logger.info("Closing Phase I/II database connections...")
        engine.dispose()


# =====================================================
# FastAPI Application
# =====================================================

# Create FastAPI application
app = FastAPI(
    title="Todo AI Chatbot API",
    description="AI-powered conversational todo management with MCP and OpenAI Agents SDK",
    version="1.0.0",
    docs_url="/docs",
    redoc_url="/redoc",
    lifespan=lifespan,
)


# =====================================================
# CORS Middleware
# =====================================================

def get_cors_origins() -> list[str]:
    """
    Get CORS origins from environment or Phase I/II settings.

    Always reads CORS_ORIGINS environment variable directly to ensure
    it works correctly on Hugging Face Spaces where settings might
    not pick up env vars at module import time.

    Returns:
        List of allowed origins
    """
    # Read directly from environment variable
    cors_origins = os.getenv(
        "CORS_ORIGINS",
        "http://localhost:3000,http://localhost:8000,https://hackathon-2-to-do-list-git-phase-3-duaapirzada22s-projects.vercel.app,https://hackathon-2-to-do-list.vercel.app"
    )
    return [origin.strip() for origin in cors_origins.split(",")]


app.add_middleware(
    CORSMiddleware,
    allow_origins=get_cors_origins(),
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# =====================================================
# Request ID Middleware (Phase III)
# =====================================================

@app.middleware("http")
async def request_id_middleware(request: Request, call_next: Callable) -> Response:
    """
    Add unique request ID to all requests for tracing.

    Request ID is added to request state and included in logs.
    """
    request_id = str(uuid.uuid4())
    request.state.request_id = request_id

    # Log request
    logger = structlog.get_logger().bind(
        request_id=request_id,
        method=request.method,
        path=request.url.path
    )
    logger.info("Request started")

    # Add request ID to response headers
    response = await call_next(request)
    response.headers["X-Request-ID"] = request_id

    logger.info("Request completed", status_code=response.status_code)

    return response


# =====================================================
# Exception Handlers
# =====================================================

@app.exception_handler(StarletteHTTPException)
async def http_exception_handler(request: Request, exc: StarletteHTTPException) -> JSONResponse:
    """
    Handle HTTP exceptions.

    Returns standardized error response with appropriate status code.
    """
    logger = structlog.get_logger().bind(
        request_id=getattr(request.state, "request_id", None),
        status_code=exc.status_code
    )

    logger.warning("HTTP exception", detail=exc.detail)

    # Use Phase I/II format if available, else Phase III format
    if PHASE_II_AVAILABLE:
        # Phase I/II format
        from fastapi import Request as FastAPIRequest
        origin = request.headers.get("origin")

        allowed_origins = get_cors_origins()
        cors_headers = {}
        if origin in allowed_origins:
            cors_headers["Access-Control-Allow-Origin"] = origin
            cors_headers["Access-Control-Allow-Credentials"] = "true"

        return JSONResponse(
            status_code=exc.status_code,
            content={"detail": exc.detail},
            headers=cors_headers
        )

    # Phase III format
    return JSONResponse(
        status_code=exc.status_code,
        content=create_error_response(
            message=exc.detail,
            code=ErrorCode.UNAUTHORIZED if exc.status_code == 401 else None
        ).model_dump()
    )


@app.exception_handler(RequestValidationError)
async def validation_exception_handler(
    request: Request,
    exc: RequestValidationError
) -> JSONResponse:
    """
    Handle validation errors.

    Returns detailed validation error response.
    """
    logger = structlog.get_logger().bind(
        request_id=getattr(request.state, "request_id", None)
    )

    logger.warning("Validation error", errors=exc.errors())

    # Use Phase I/II format if available, else Phase III format
    if PHASE_II_AVAILABLE:
        from fastapi import Request as FastAPIRequest
        origin = request.headers.get("origin")

        allowed_origins = get_cors_origins()
        cors_headers = {}
        if origin in allowed_origins:
            cors_headers["Access-Control-Allow-Origin"] = origin
            cors_headers["Access-Control-Allow-Credentials"] = "true"

        return JSONResponse(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            content={"detail": exc.errors()},
            headers=cors_headers
        )

    # Phase III format
    return JSONResponse(
        status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
        content=create_validation_error_response(exc.errors()).model_dump()
    )


@app.exception_handler(Exception)
async def general_exception_handler(request: Request, exc: Exception) -> JSONResponse:
    """
    Handle all other exceptions.

    Returns generic error response without exposing internal details.
    """
    logger = structlog.get_logger().bind(
        request_id=getattr(request.state, "request_id", None)
    )

    logger.error("Unhandled exception", error=str(exc), type=type(exc).__name__)

    # Use Phase I/II format if available, else Phase III format
    if PHASE_II_AVAILABLE:
        from fastapi import Request as FastAPIRequest
        origin = request.headers.get("origin")

        allowed_origins = get_cors_origins()
        cors_headers = {}
        if origin in allowed_origins:
            cors_headers["Access-Control-Allow-Origin"] = origin
            cors_headers["Access-Control-Allow-Credentials"] = "true"

        return JSONResponse(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            content={"detail": str(exc)},
            headers=cors_headers
        )

    # Phase III format
    return JSONResponse(
        status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
        content=create_error_response(
            message="An unexpected error occurred",
            code=ErrorCode.INTERNAL_ERROR
        ).model_dump()
    )


# =====================================================
# Health Check Endpoint
# =====================================================

@app.get("/health", response_model=HealthResponse, tags=["Health"])
async def health_check():
    """
    Health check endpoint.

    Returns service status, database connection, and MCP server status.
    """
    logger = structlog.get_logger()

    # Check database connection
    db_status = "connected" if await check_db_connection() else "disconnected"

    # Check MCP server
    try:
        mcp_server = get_mcp_server()
        mcp_status = f"initialized ({len(mcp_server.list_tools())} tools)"
    except Exception:
        mcp_status = "not initialized"

    logger.info("Health check", database=db_status, mcp_server=mcp_status)

    return HealthResponse(
        status="healthy",
        version="1.0.0",
        database=db_status,
        mcp_server=mcp_status
    )


# =====================================================
# Root Endpoint
# =====================================================

@app.get("/", tags=["Root"])
async def root():
    """
    Root endpoint with API information.
    """
    return {
        "name": "Todo AI Chatbot API",
        "version": "1.0.0",
        "description": "AI-powered conversational todo management",
        "phase_ii_available": PHASE_II_AVAILABLE,
        "docs": "/docs",
        "health": "/health"
    }


# =====================================================
# Phase I/II Routes (if available)
# =====================================================

if PHASE_II_AVAILABLE:
    # Include Phase I/II routers
    app.include_router(auth.router, prefix=settings.API_PREFIX, tags=["auth"])
    app.include_router(tasks.router, prefix=settings.API_PREFIX, tags=["tasks"])


# =====================================================
# Phase III Routes
# =====================================================

# Chat router (User Story 1 - MVP)
try:
    from backend.src.api.chat import router as chat_router
    app.include_router(chat_router, tags=["Chat"])
except ImportError:
    try:
        from src.api.chat import router as chat_router
        app.include_router(chat_router, tags=["Chat"])
    except ImportError as e:
        logger = structlog.get_logger()
        logger.warning("Chat router not available", error=str(e))


# =====================================================
# Run Directly
# =====================================================

if __name__ == "__main__":
    import uvicorn

    # Use Phase I/II settings if available, else Phase III defaults
    if PHASE_II_AVAILABLE:
        host = settings.API_HOST
        port = settings.API_PORT
        reload = settings.DEBUG
    else:
        host = os.getenv("API_HOST", "0.0.0.0")
        port = int(os.getenv("API_PORT", "8000"))
        reload = os.getenv("APP_ENV", "development") == "development"

    uvicorn.run(
        "src.main:app",
        host=host,
        port=port,
        reload=reload
    )
