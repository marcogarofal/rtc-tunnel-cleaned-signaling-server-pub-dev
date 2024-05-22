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
        if session and not session.closed:
            await session.send(message)
            return True
        return False

    def add_session(self, session_id, session, topic, role):
        logging.info(f"New {role} client [{session_id}] connected to topic [{topic}]")
        self.sessions[session_id] = session
        if topic not in self.topics:
            if role == "server":
                self.topics[topic] = {"sessions": [], "message_count": 0}
            else:
                logging.warning(f"Client [{session_id}] tried to connect to non-existent topic [{topic}]")
                return False
        self.topics[topic]["sessions"].append(session)
        return True

    def remove_session(self, session_id, topic):
        logging.info(f"Client [{session_id}] disconnected from topic [{topic}]")
        if session_id in self.sessions:
            session = self.sessions.pop(session_id, None)
            if session and topic in self.topics:
                if session in self.topics[topic]["sessions"]:
                    self.topics[topic]["sessions"].remove(session)
                if not self.topics[topic]["sessions"]:
                    del self.topics[topic]
                    print(self.topics[topic])

    def get_session_ids(self):
        return self.sessions.keys()
    
    def get_topics(self):
        return self.topics

    def get_sessions_by_topic(self, topic):
        return self.topics.get(topic, {}).get("sessions", [])

    def increment_message_count(self, topic):
        if topic in self.topics:
            self.topics[topic]["message_count"] += 1
            return self.topics[topic]["message_count"]
        return 0

    def cleanup(self):
        for session_id, session in list(self.sessions.items()):
            if session.closed:
                topic = next((t for t, s in self.topics.items() if session in s["sessions"]), None)
                if topic:
                    self.remove_session(session_id, topic)

async def message_topic_websocket_handler(websocket, path, message_service):
    components = path.split('/')
    role = components[-2]
    topic = components[-1]
    session_id = id(websocket)
    if not message_service.add_session(session_id, websocket, topic, role):
        await websocket.close()
        return

    try:
        async for message in websocket:
            print("\n\n--topic:", message_service.get_topics())
            print("\n--topic:", message_service.get_sessions_by_topic(topic))
            logging.info(f"Message received on topic [{topic}] by {role}: {message}")
            target_sessions = message_service.get_sessions_by_topic(topic)
            
            
            # Increment the message count for the topic
            message_count = message_service.increment_message_count(topic)
            if message_count > 2:
                logging.info(f"Message limit reached for topic [{topic}]. Removing topic.")
                for target_ws in list(target_sessions):
                    target_ws_id = id(target_ws)
                    message_service.remove_session(target_ws_id, topic)
                print("\n\ntopic:", message_service.get_topics())
                target_sessions = message_service.get_sessions_by_topic(topic)
                print("\ntarget_sessions:", target_sessions)
                break
            
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
