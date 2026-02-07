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

# STARTUP MARKER - This proves the latest code is loaded
import datetime
print(f"[BACKEND STARTUP] Loading main.py at {datetime.datetime.now()}")

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
# OpenAPI Security Scheme Configuration
# =====================================================

# Custom OpenAPI schema with JWT Bearer security scheme
def custom_openapi():
    if app.openapi_schema:
        return app.openapi_schema
    from fastapi.openapi.utils import get_openapi
    openapi_schema = get_openapi(
        title=app.title,
        version=app.version,
        description=app.description,
        routes=app.routes,
    )
    # Add JWT Bearer security scheme
    openapi_schema["components"]["securitySchemes"] = {
        "BearerAuth": {
            "type": "http",
            "scheme": "bearer",
            "bearerFormat": "JWT",
            "description": "Enter your JWT token (without 'Bearer ' prefix). Get token from /api/auth/signin or /api/auth/signup"
        }
    }
    # Apply security to all routes that need it (chat endpoints)
    for path, path_item in openapi_schema["paths"].items():
        for method in path_item.values():
            if "operationId" in method:
                # Add security requirement to endpoints that need auth
                if any(x in path for x in ["/api/", "/chat"]):
                    method.setdefault("security", []).append({"BearerAuth": []})
    app.openapi_schema = openapi_schema
    return app.openapi_schema

app.openapi = custom_openapi


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
# Health Check Endpoints
# =====================================================

@app.get("/health/live", tags=["Health"])
async def liveness_probe():
    """
    Liveness probe - lightweight check if the app is running.

    Kubernetes liveness probes use this to detect if the container
    needs to be restarted. This endpoint should always return 200
    if the application is running, regardless of database state.

    Returns:
        Simple alive status - no database check
    """
    return {"status": "alive"}


@app.get("/health/ready", tags=["Health"])
async def readiness_probe():
    """
    Readiness probe - check if the app is ready to serve traffic.

    Kubernetes readiness probes use this to determine if the pod
    should receive traffic. Returns 503 if database is not ready.

    Returns:
        Service ready status with database connection check
    """
    logger = structlog.get_logger()

    # Check database connection
    db_ready = await check_db_connection()

    if not db_ready:
        logger.warning("Readiness check failed - database not ready")
        # Return 503 to indicate not ready
        from fastapi import status as http_status
        from fastapi.responses import JSONResponse
        return JSONResponse(
            status_code=http_status.HTTP_503_SERVICE_UNAVAILABLE,
            content={
                "status": "not_ready",
                "database": "disconnected"
            }
        )

    logger.info("Readiness check passed")

    return {
        "status": "ready",
        "database": "connected"
    }


@app.get("/health", response_model=HealthResponse, tags=["Health"])
async def health_check():
    """
    Comprehensive health check endpoint.

    Returns service status, database connection, and MCP server status.
    This is the main health endpoint for monitoring and debugging.
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

# ChatKit session router (for getClientSecret mode)
try:
    from backend.src.api.chatkit_session import router as chatkit_session_router
    app.include_router(chatkit_session_router, tags=["ChatKit"])
except ImportError:
    try:
        from src.api.chatkit_session import router as chatkit_session_router
        app.include_router(chatkit_session_router, tags=["ChatKit"])
    except ImportError as e:
        logger = structlog.get_logger()
        logger.warning("ChatKit session router not available", error=str(e))

# Simple chat router (no database dependency)
try:
    from backend.src.api.simple_chat import router as simple_chat_router
    app.include_router(simple_chat_router, tags=["Chat"])
except ImportError:
    try:
        from src.api.simple_chat import router as simple_chat_router
        app.include_router(simple_chat_router, tags=["Chat"])
    except ImportError as e:
        logger = structlog.get_logger()
        logger.warning("Simple chat router not available", error=str(e))

# Direct chat router (working solution - calls MCP tools directly)
try:
    from backend.src.api.direct_chat import router as direct_chat_router
    app.include_router(direct_chat_router, tags=["Chat"])
except ImportError:
    try:
        from src.api.direct_chat import router as direct_chat_router
        app.include_router(direct_chat_router, tags=["Chat"])
    except ImportError as e:
        logger = structlog.get_logger()
        logger.warning("Direct chat router not available", error=str(e))

# =====================================================
# ChatKit Server Endpoint (Self-hosted, no file scopes required)
# =====================================================

# Create ChatKit server instance (singleton)
_chatkit_server = None

def get_chatkit_server():
    """Get or create the ChatKit server instance."""
    global _chatkit_server
    if _chatkit_server is None:
        try:
            from backend.src.chatkit.server import create_chatkit_server
        except ImportError:
            from src.chatkit.server import create_chatkit_server

        _chatkit_server = create_chatkit_server()

        logger = structlog.get_logger()
        logger.info("ChatKit server initialized")
    return _chatkit_server


@app.post("/chatkit")
async def chatkit_endpoint(request: Request):
    """
    Main ChatKit endpoint for processing all ChatKit requests.

    This endpoint handles ChatKit protocol requests from the frontend.
    It streams responses using Server-Sent Events (SSE) for real-time updates.

    The ChatKit server handles:
    - Thread creation and retrieval
    - Message processing and streaming
    - Tool execution (task management tools)
    - User-scoped data isolation

    Authentication: Bearer token required (from Authorization header or query param)
    """
    # Debug: trigger reload
    from fastapi.responses import StreamingResponse, Response
    from chatkit.server import StreamingResult
    from src.auth.middleware import extract_token_from_header_or_query_manual

    # Debug logging
    print("=" * 80)
    print(f"[DEBUG /chatkit] Request received at {datetime.datetime.now()}")
    print(f"[DEBUG /chatkit] Headers: {dict(request.headers)}")

    # Get user ID from token for context
    auth_header = request.headers.get("Authorization")
    token = request.query_params.get("token")

    user_id = extract_token_from_header_or_query_manual(auth_header, token)

    print(f"[DEBUG /chatkit] Extracted user_id: {user_id}")

    # Build request context with user_id
    context = {
        "user_id": user_id,
        "request": request
    }

    logger = structlog.get_logger().bind(user_id=user_id)
    logger.info("ChatKit request received")

    # Get request body
    body = await request.body()
    print(f"[DEBUG /chatkit] Request body length: {len(body)} bytes")
    print(f"[DEBUG /chatkit] Request body (raw): {body[:1000].decode('utf-8', errors='ignore')}")

    # Get ChatKit server and process request
    server = get_chatkit_server()
    print(f"[DEBUG /chatkit] About to call server.process")
    result = await server.process(body, context)
    print(f"[DEBUG /chatkit] server.process returned, result type: {type(result).__name__}")

    # Return appropriate response based on result type
    if isinstance(result, StreamingResult):
        print(f"[DEBUG /chatkit] Returning StreamingResponse (SSE)")
        print("=" * 80)
        return StreamingResponse(result, media_type="text/event-stream")
    else:
        print(f"[DEBUG /chatkit] Returning JSON response")
        print(f"[DEBUG /chatkit] Response preview: {result.json[:200].decode('utf-8', errors='ignore')}")
        print("=" * 80)
        return Response(content=result.json, media_type="application/json")


@app.post("/chatkit/{path:path}")
async def chatkit_catchall(request: Request, path: str):
    """
    Catch-all endpoint for ChatKit requests to subpaths.

    ChatKit React may make requests to /chatkit/messages, /chatkit/threads, etc.
    This endpoint routes all of them to the ChatKit server.
    """
    print(f"[DEBUG /chatkit/{path}] Received request to subpath")
    # Forward to the main chatkit endpoint handler
    return await chatkit_endpoint(request)


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
