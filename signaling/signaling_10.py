import asyncio
import websockets
import logging

logging.basicConfig(level=logging.INFO)

class MessageService:
    def __init__(self):
        self.sessions = {}
        self.topics = {}

    async def send(self, destination, message):
        logging.info(f"Sending message [{message}] to [{destination}]")

        session = self.sessions.get(destination)
        if session:
            await session.send(message)
            return True

        return False

    def add_session(self, session_id, session, topic):
        logging.info(f"New client [{session_id}] connected to topic [{topic}]")
        self.sessions[session_id] = session
        if topic not in self.topics:
            self.topics[topic] = []
        self.topics[topic].append(session)

    def remove_session(self, session_id, topic):
        logging.info(f"Client [{session_id}] disconnected from topic [{topic}]")
        if session_id in self.sessions:
            session = self.sessions[session_id]
            if topic in self.topics and session in self.topics[topic]:
                self.topics[topic].remove(session)
                if not self.topics[topic]:
                    del self.topics[topic]
            del self.sessions[session_id]

    def get_session_ids(self):
        return self.sessions.keys()

    def get_sessions_by_topic(self, topic):
        return self.topics.get(topic, [])

    def cleanup(self):
        for session_id, session in list(self.sessions.items()):
            if session.closed:
                topic = next((t for t, s in self.topics.items() if session in s), None)
                if topic:
                    self.remove_session(session_id, topic)


async def message_topic_websocket_handler(websocket, path, message_service):
    topic = path.split('/')[-1]
    session_id = id(websocket)
    message_service.add_session(session_id, websocket, topic)
    try:
        async for message in websocket:
            logging.info(f"Message received on topic [{topic}]: {message}")
            target_sessions = message_service.get_sessions_by_topic(topic)
            for target_ws in target_sessions:
                if target_ws != websocket and not target_ws.closed:
                    await target_ws.send(message)
    except websockets.exceptions.ConnectionClosed:
        logging.info("Connection closed")
    finally:
        message_service.remove_session(session_id, topic)
        message_service.cleanup()


async def main():
    global message_service
    message_service = MessageService()

    async def handler(websocket, path):
        await message_topic_websocket_handler(websocket, path, message_service)

    async with websockets.serve(handler, '0.0.0.0', 8080):
        await asyncio.Future()

async def keep_alive():
    while True:
        await asyncio.sleep(3600)

if __name__ == "__main__":
    asyncio.run(main())
