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

async def message_topic_websocket_handler(websocket, path):
    try:
        async for message in websocket:  # Attendere i messaggi in arrivo dalla connessione WebSocket
            print(f"Message received: {message}")  # Stampa il messaggio ricevuto
            # Gestisci il messaggio ricevuto come desiderato...
    except websockets.exceptions.ConnectionClosedOK:
        print("Connection closed by client")

async def main():
    global message_service
    message_service = MessageService()
    
    async with websockets.serve(message_topic_websocket_handler, '127.0.0.1', 8080):
        await asyncio.Future()  # Mantieni il server in esecuzione
        
    #start_server = await websockets.serve(
        #lambda websocket, path: message_topic_websocket_handler(websocket, path, message_service),
        #'127.0.0.1', 8080)

    #app = web.Application()
    
    #app.router.add_post("/message", message_handler)
    #app.router.add_post('/message/{dest}', message_handler)  # Definisci il gestore per le richieste POST all'endpoint /message/{dest}

    
    #runner = web.AppRunner(app)
    #await runner.setup()
    #site = web.TCPSite(runner, '127.0.0.1', 8081)
    #await site.start()

    #await asyncio.gather(
        #start_server.wait_closed(),
        #keep_alive()
    #)

async def keep_alive():
    while True:
        await asyncio.sleep(3600)
        




#if __name__ == "__main__":
asyncio.run(main())

