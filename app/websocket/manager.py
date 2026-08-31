from collections import defaultdict

from fastapi import WebSocket


class ConnectionManager:
    def __init__(self):
        self.rooms: dict[str, set[WebSocket]] = defaultdict(set)

    async def connect(
        self,
        room_id: str,
        websocket: WebSocket,
    ):
        await websocket.accept()
        self.rooms[room_id].add(websocket)

    def disconnect(
        self,
        room_id: str,
        websocket: WebSocket,
    ):
        connections = self.rooms.get(room_id)

        if connections is None:
            return

        connections.discard(websocket)

        if not connections:
            del self.rooms[room_id]

    async def broadcast(
        self,
        room_id: str,
        message: dict,
    ):
        connections = self.rooms.get(room_id)

        if not connections:
            return

        disconnected = []

        for websocket in connections:
            try:
                await websocket.send_json(message)
            except Exception:
                disconnected.append(websocket)

        for websocket in disconnected:
            self.disconnect(room_id, websocket)


manager = ConnectionManager()