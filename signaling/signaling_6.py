import asyncio
import websockets
import logging

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

async def main():
    message_service = MessageService()
    start_server = await websockets.serve(
        lambda websocket, path: message_topic_websocket_handler(websocket, path, message_service),
        '127.0.0.1', 8080)
    await start_server.wait_closed()

async def keep_alive():
    while True:
        await asyncio.sleep(3600)

if __name__ == "__main__":
    asyncio.run(main())

