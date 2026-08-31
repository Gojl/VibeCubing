import asyncio
import json
import websockets

URI = "ws://127.0.0.1:8000/ws/rooms/q_06eB9R57su"


async def main():
    async with websockets.connect(URI) as websocket:
        print("JAN CONNECTED")

        await websocket.send(json.dumps({
            "type": "test",
            "from": "Amad",
        }))

        while True:
            message = await websocket.recv()
            print("JAN RECEIVED:", message)


asyncio.run(main())