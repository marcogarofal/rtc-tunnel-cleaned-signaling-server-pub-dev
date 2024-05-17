import asyncio
import websockets

#async def send_data():
    #async with websockets.connect('ws://127.0.0.1:8080') as websocket:  # Sostituisci con l'URL del tuo server WebSocket
        #data = '{"data": "Hello, WebSocket!"}'  # Dati da inviare (puoi sostituire con i tuoi dati)
        #await websocket.send(data)
        #print(f"Data sent: {data}")


async def send_data():
    async with websockets.connect('ws://127.0.0.1:8080/message/server') as websocket:  # Sostituisci con l'URL del tuo server WebSocket
        data = '{"data": "Hello, WebSocket!"}'  # Dati da inviare (puoi sostituire con i tuoi dati)
        await websocket.send(data)
        print(f"Data sent: {data}")

asyncio.run(send_data())



