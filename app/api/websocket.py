from fastapi import APIRouter, WebSocket, WebSocketDisconnect

from app.websocket.manager import manager


router = APIRouter(tags=["websocket"])


@router.websocket("/ws/rooms/{room_id}")
async def websocket_endpoint(
    websocket: WebSocket,
    room_id: str,
):
    await manager.connect(room_id, websocket)

    try:
        while True:
            data = await websocket.receive_json()

            await manager.broadcast(
                room_id,
                data,
            )

    except WebSocketDisconnect:
        manager.disconnect(room_id, websocket)