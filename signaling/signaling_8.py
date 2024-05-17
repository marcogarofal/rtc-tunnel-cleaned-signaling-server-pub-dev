import asyncio
import websockets
import logging
from aiohttp import web

logging.basicConfig(level=logging.INFO)

class MessageService:
    def __init__(self):
        self.sessions = {}

    async def send(self, destination, message):
        logging.info(f"Sending message [{message}] to [{destination}]")

        session = self.sessions.get(destination)
        if session:
            await session.send(message)
            return True

        return False

    def add_session(self, session_id, session):
        logging.info(f"New client [{session_id}] connected")
        self.sessions[session_id] = session

    def remove_session(self, session_id):
        logging.info(f"Client [{session_id}] disconnected")
        if session_id in self.sessions:
            del self.sessions[session_id]

    def get_session_ids(self):
        return self.sessions.keys()

async def message_topic_websocket_handler(websocket, path, message_service):
    session_id = path.rsplit('/', 1)[-1]
    message_service.add_session(session_id, websocket)
    try:
        await asyncio.wait([websocket.wait_closed()])
    finally:
        message_service.remove_session(session_id)

async def state(websocket, path, message_service):
    session_ids = message_service.get_session_ids()
    await websocket.send('\n'.join(session_ids))


from aiohttp import web

active_websockets = set()

async def forward_message(message, target_websocket):
    await target_websocket.send(message)


async def get_target_websockets(source_websocket):
    # Ritorna tutti i WebSocket attivi tranne quello che ha inviato la richiesta
    return [ws for ws in active_websockets if ws != source_websocket]

async def message_topic_websocket_handler(websocket, path):
    active_websockets.add(websocket)  # Aggiungi la WebSocket appena connessa all'elenco delle WebSocket attive
    try:
        async for message in websocket:
            print(f"Message received: {message}")
            
            # Ottieni tutti i WebSocket attivi tranne quello che ha inviato la richiesta
            target_websockets = await get_target_websockets(websocket)
            
            # Inoltra il messaggio a tutti i WebSocket tranne quello che ha inviato la richiesta
            for target_ws in target_websockets:
                await forward_message(message, target_ws)
            
    except websockets.exceptions.ConnectionClosedOK:
        print("Connection closed by client")
    finally:
        active_websockets.remove(websocket)  # Rimuovi la WebSocket dall'elenco delle WebSocket attive quando viene chiusa

async def print_active_websockets():
    while True:
        print("Active Websockets:")
        for ws in active_websockets:
            print(ws.remote_address)
        await asyncio.sleep(10)  # Stampa l'elenco delle WebSocket attive ogni 10 secondi


async def main():
    global message_service
    message_service = MessageService()
    
    async with websockets.serve(message_topic_websocket_handler, '127.0.0.1', 8080):
        await asyncio.Future()  # Mantieni il server in esecuzione
        



async def keep_alive():
    while True:
        await asyncio.sleep(3600)
        




#if __name__ == "__main__":
asyncio.run(main())

