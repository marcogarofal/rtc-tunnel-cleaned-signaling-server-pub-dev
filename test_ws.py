import asyncio
import websockets

async def main():
    async with websockets.connect('ws://127.0.0.1:8080/topic/message/server') as websocket:
        await websocket.send('Test message')
        response = await websocket.recv()
        print('Response from server:', response)

asyncio.run(main())
