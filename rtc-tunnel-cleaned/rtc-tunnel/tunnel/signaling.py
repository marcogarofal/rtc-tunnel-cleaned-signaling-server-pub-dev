from .aiortc_source import RTCSessionDescription, RTCIceCandidate

from .aiortc_source.sdp import candidate_from_sdp, candidate_to_sdp


import asyncio
import json
import sys
import requests
import websockets
from json import JSONDecodeError



class ConsoleSignaling:
    def __init__(self, source: str):
        self._source = source
        self._read_pipe = sys.stdin
        self._read_transport = None
        self._reader = None
        self._write_pipe = sys.stdout

    async def connect_async(self):
        loop = asyncio.get_event_loop()
        self._reader = asyncio.StreamReader(loop=loop)
        self._read_transport, _ = await loop.connect_read_pipe(
            lambda: asyncio.StreamReaderProtocol(self._reader),
            self._read_pipe)

    async def close_async(self):
        if self._reader is not None:
            self._read_transport.close()

    async def receive_async(self):
        print('-- Please enter a message from remote party to [%s] --' % self._source)
        while True:
            data = await self._reader.readline()
            try:
                message = data.decode(self._read_pipe.encoding)
                obj, source = object_from_string(message)
                print()
                return obj, source
            except JSONDecodeError:
                pass

    def send(self, descr, dest: str):
        print('-- Please send this message to the remote party named [%s] --' % dest)
        message = object_to_string(descr, self._source)
        self._write_pipe.write(message + '\n')
        print()


class WebSignaling:
    def __init__(self, source: str, send_url: str, receive_url: str, topic: str):
        self._source = source
        self._send_url = send_url
        self._receive_url = receive_url
        self._client = None
        self._topic = topic

    async def connect_async(self):
        #print(self._receive_url  + '/topic/message/' + self._source)
        #self._client = await websockets.connect(self._receive_url + '/topic/message/' + self._source)
        print(self._receive_url  + '/topic/message/' + self._source + '/' + self._topic) 
        self._client = await websockets.connect(self._receive_url + '/topic/message/' + self._source + '/' + self._topic) 
        return self._client

    async def close_async(self):
        if self._client is not None:
            await self._client.close()

    async def receive_async(self):
        print("receive async")
        message = await self._client.recv()
        print("\n\nmessage: ", message)
        # if object_from_string(message) != None:
        #     print("\n\nA")
        #     return object_from_string(message)
        # else:
        #     print("\n\nB")
        return object_from_string(message, self._topic)

    def send(self, descr, dest: str):
        message = object_to_string(descr, self._source)
      
        print(self._send_url + '/message/' + dest+"\n\n")
        print(message)
        print("type:", type(self._client))
        #await websocket.send(data)
        print(f"Data sent: {data}")
        #response = requests.post(self._send_url + '/message/' + dest, data=message)
        if response.status_code != 200:
            raise IOError('Unable to send signaling message: ' + str(response.status_code))
    
    async def send_data(self, websocket, descr, dest: str):
        data = object_to_string(descr, self._source)
        #data = '{"message": "Hello, WebSocket!"}'  # Dati da inviare (puoi sostituire con i tuoi dati)
        await websocket.send(data)
        print(f"\n\nData sent: {data}")


def object_to_string(obj, source: str):
    print("obj2:", obj)
    if isinstance(obj, RTCSessionDescription):
        data = {
            'sdp': obj.sdp,
            'type': obj.type,
            'topic': obj.topic
            #'topic': "topic1"
        }
    elif isinstance(obj, RTCIceCandidate):
        data = {
            'candidate': 'candidate:' + candidate_to_sdp(obj),
            'id': obj.sdpMid,
            'label': obj.sdpMLineIndex,
            'type': 'candidate',
        }
    else:
        raise ValueError('Can only send RTCSessionDescription or RTCIceCandidate')
    message = {
        'source': source,
        'data': data
    }
    print("\n\n::", message)
    return json.dumps(message, sort_keys=True)


def object_from_string(message_str, topic):
    obj = json.loads(message_str)
    
    print("\n\nobj:",obj)
    
    data = obj['data']
    source = obj['source']

    print("\ndebug:", data)
    if data['type'] in ['answer', 'offer']:  
        if data['topic']==topic:  
            print("\n\nquii")
            return RTCSessionDescription(**data), source
        else:
            print("not matching topics")
            return None
            #raise ValueError('not matching topics')
    elif data['type'] == 'candidate':
        candidate = candidate_from_sdp(data['candidate'].split(':', 1)[1])
        candidate.sdpMid = data['id']
        candidate.sdpMLineIndex = data['label']
        return candidate, source
