"""
WebSocket/SSE API for real-time task updates (User Story 4)
Broadcasts task updates to all connected clients
"""

import logging
import asyncio
import json
from typing import Dict, Set, Any, Optional
from datetime import datetime
from fastapi import APIRouter, WebSocket, WebSocketDisconnect, Request
from fastapi.responses import StreamingResponse
from collections import defaultdict

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/realtime", tags=["realtime"])


# Connection state management (T056)
class ConnectionManager:
    """
    Manages WebSocket/SSE connections for real-time updates
    """

    def __init__(self):
        # Active connections: {user_id: Set[websockets]}
        self.active_connections: Dict[int, Set[WebSocket]] = defaultdict(set)

        # Connection metadata: {websocket: {user_id, connected_at}}
        self.connection_metadata: Dict[WebSocket, Dict[str, Any]] = {}

        # Event queues for SSE: {user_id: Queue}
        self.event_queues: Dict[int, asyncio.Queue] = {}

        # Missed events buffer for reconnection (T062)
        self.missed_events: Dict[int, list] = defaultdict(list)

    async def connect(self, websocket: WebSocket, user_id: int):
        """Accept a new WebSocket connection"""
        await websocket.accept()
        self.active_connections[user_id].add(websocket)
        self.connection_metadata[websocket] = {
            "user_id": user_id,
            "connected_at": datetime.utcnow()
        }
        logger.info(f"WebSocket connected: user_id={user_id}")

    def disconnect(self, websocket: WebSocket):
        """Remove a WebSocket connection"""
        metadata = self.connection_metadata.pop(websocket, None)
        if metadata:
            user_id = metadata["user_id"]
            self.active_connections[user_id].discard(websocket)
            logger.info(f"WebSocket disconnected: user_id={user_id}")

    async def broadcast_to_user(self, user_id: int, message: dict):
        """Send a message to all connections for a specific user"""
        if user_id not in self.active_connections:
            # Store missed event for reconnection (T062)
            self.missed_events[user_id].append({
                "message": message,
                "timestamp": datetime.utcnow().isoformat()
            })

            # Keep only last 100 missed events per user
            if len(self.missed_events[user_id]) > 100:
                self.missed_events[user_id] = self.missed_events[user_id][-100:]

            return

        # Remove from queue
        if user_id in self.missed_events:
            del self.missed_events[user_id]

        # Send to all active connections
        for connection in list(self.active_connections[user_id]):
            try:
                await connection.send_json(message)
            except Exception as e:
                logger.warning(f"Error sending to connection: {e}")
                self.disconnect(connection)

    async def get_missed_events(self, user_id: int) -> list:
        """Get missed events for a user (for reconnection sync)"""
        events = self.missed_events.get(user_id, [])
        self.missed_events[user_id] = []
        return events

    def get_connection_count(self, user_id: int) -> int:
        """Get number of active connections for a user"""
        return len(self.active_connections.get(user_id, set()))


# Global connection manager
_manager: Optional[ConnectionManager] = None


def get_connection_manager() -> ConnectionManager:
    """Get or create the global ConnectionManager"""
    global _manager
    if _manager is None:
        _manager = ConnectionManager()
    return _manager


# WebSocket endpoint (T054-T057)
@router.websocket("/ws")
async def websocket_endpoint(websocket: WebSocket, token: Optional[str] = None):
    """
    WebSocket endpoint for real-time task updates

    Query parameters:
        token: JWT authentication token
    """
    # Authenticate user from token
    user_id = 1  # TODO: Extract from JWT token

    manager = get_connection_manager()
    await manager.connect(websocket, user_id)

    try:
        # Send missed events on connection (T062)
        missed_events = await manager.get_missed_events(user_id)
        if missed_events:
            await websocket.send_json({
                "type": "sync",
                "events": missed_events
            })

        # Keep connection alive and handle incoming messages
        while True:
            data = await websocket.receive_text()

            # Handle ping/pong for keep-alive
            if data == "ping":
                await websocket.send_text("pong")

    except WebSocketDisconnect:
        manager.disconnect(websocket)
    except Exception as e:
        logger.error(f"WebSocket error: {e}")
        manager.disconnect(websocket)


# SSE endpoint alternative (T055)
@router.get("/sse")
async def sse_endpoint(request: Request, token: Optional[str] = None):
    """
    Server-Sent Events endpoint for real-time updates

    Alternative to WebSocket for clients that prefer SSE
    """
    # Authenticate user from token
    user_id = 1  # TODO: Extract from JWT token

    async def event_stream():
        """Generate SSE events"""
        manager = get_connection_manager()

        # Create a queue for this user
        if user_id not in manager.event_queues:
            manager.event_queues[user_id] = asyncio.Queue()

        queue = manager.event_queues[user_id]

        try:
            # Send initial connection event
            yield f"event: connected\ndata: {{'user_id': {user_id}, 'timestamp': '{datetime.utcnow().isoformat()}'}}\n\n"

            # Stream events
            while True:
                # Wait for events (with timeout for keep-alive)
                try:
                    event = await asyncio.wait_for(queue.get(), timeout=30)
                    yield f"event: {event['type']}\ndata: {json.dumps(event['data'])}\n\n"
                except asyncio.TimeoutError:
                    # Send keep-alive comment
                    yield ": keep-alive\n\n"

        except asyncio.CancelledError:
            logger.info(f"SSE stream closed for user {user_id}")
        finally:
            # Clean up queue
            if user_id in manager.event_queues:
                del manager.event_queues[user_id]

    return StreamingResponse(
        event_stream(),
        media_type="text/event-stream",
        headers={
            "Cache-Control": "no-cache",
            "Connection": "keep-alive",
            "X-Accel-Buffering": "no"
        }
    )


# Health check
@router.get("/health")
async def health_check():
    """Health check endpoint for real-time service"""
    manager = get_connection_manager()
    return {
        "status": "healthy",
        "active_connections": sum(len(conns) for conns in manager.active_connections.values())
    }
