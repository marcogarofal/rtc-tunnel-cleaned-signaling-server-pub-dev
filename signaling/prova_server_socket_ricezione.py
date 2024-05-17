import asyncio
import websockets

async def message_topic_websocket_handler(websocket, path):
    try:
        async for message in websocket:  # Attendere i messaggi in arrivo dalla connessione WebSocket
            print(f"Message received: {message}")  # Stampa il messaggio ricevuto
            # Gestisci il messaggio ricevuto come desiderato...
    except websockets.exceptions.ConnectionClosedOK:
        print("Connection closed by client")

async def main():
    async with websockets.serve(message_topic_websocket_handler, '127.0.0.1', 8080):
        await asyncio.Future()  # Mantieni il server in esecuzione

asyncio.run(main())
