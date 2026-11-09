import json
import asyncio
from typing import List
from fastapi import APIRouter, WebSocket, WebSocketDisconnect

router = APIRouter(tags=["WebSockets Live Feed"])

class ActivityFeedManager:
    def __init__(self):
        self.active_connections: List[WebSocket] = []

    async def connect(self, websocket: WebSocket):
        await websocket.accept()
        self.active_connections.append(websocket)

    def disconnect(self, websocket: WebSocket):
        if websocket in self.active_connections:
            self.active_connections.remove(websocket)

    async def broadcast_event(self, event_type: str, message: str, metadata: dict = None):
        payload = json.dumps({
            "event_type": event_type,
            "message": message,
            "metadata": metadata or {},
            "timestamp": asyncio.get_event_loop().time()
        })
        for connection in list(self.active_connections):
            try:
                await connection.send_text(payload)
            except Exception:
                self.disconnect(connection)

activity_ws_manager = ActivityFeedManager()

@router.websocket("/ws/activity")
async def websocket_activity_feed(websocket: WebSocket):
    await activity_ws_manager.connect(websocket)
    try:
        while True:
            # Keep-alive heartbeat
            data = await websocket.receive_text()
            if data == "ping":
                await websocket.send_text("pong")
    except WebSocketDisconnect:
        activity_ws_manager.disconnect(websocket)

