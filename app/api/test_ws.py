import asyncio
import websockets

URI = "ws://127.0.0.1:8000/ws/rooms/q_06eB9R57su"


async def main():
    async with websockets.connect(URI) as websocket:
        print("CONNECTED")

        await websocket.send('{"type":"test","message":"hello"}')
        print("SENT")

        while True:
            message = await websocket.recv()
            print("RECEIVED:", message)


asyncio.run(main())