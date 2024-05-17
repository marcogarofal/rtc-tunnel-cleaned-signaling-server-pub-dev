import asyncio
import websockets

async def hello():
    async with websockets.connect('ws://localhost:8080/message/server') as websocket:
        await websocket.send("Hello, WebSocket!")
        response = await websocket.recv()
        print(response)

asyncio.run(hello())

