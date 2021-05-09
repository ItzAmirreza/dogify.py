from asyncio import events
from asyncio.events import AbstractEventLoop
from types import FunctionType
import websockets
import asyncio
import json
from .event import EventHandler
from ..core.constants import constants

heartBeatInterval = constants['heartBeatInterval']


class Connection:
    def __init__(self,
                 uri: str,
                 events: dict[str, dict],
                 commands: dict[str, FunctionType],
                 loop: AbstractEventLoop,
                 handlers: dict[str, FunctionType],
                 prefix: str,
                 tick: int):

        self.uri = uri
        self.event_handler = EventHandler(events, commands, handlers, prefix)
        self.loop = loop
        self.prefix = prefix
        self.listeners = {}
        self.tick = tick

    async def initialize(self):
        self.ws = await websockets.connect(self.uri)
        asyncio.ensure_future(self.heartBeat()),
        asyncio.ensure_future(self.socktGateway())

    async def heartBeat(self):
        await asyncio.sleep(heartBeatInterval/1000)
        await self.ws.ping()
        await self.event_handler.run('on_ping')
        while True:
            await asyncio.sleep(heartBeatInterval/1000)
            await self.ws.ping()

    async def send(self, data):
        await self.ws.send(data)

    async def get(self, ref):
        async def recieve():
            self.listeners[ref] = None
            while True:
                await asyncio.sleep(self.tick)
                if not self.listeners[ref] == None:
                    res = self.listeners[ref]
                    self.listeners.pop(ref)
                    return res
        res = await self.loop.create_task(recieve())
        return res

    async def socktGateway(self):
        async for msg in self.ws:
            if not msg == 'pong':
                loaded_msg = json.loads(msg)

                if 'error' in loaded_msg:
                    raise Exception(loaded_msg['d']['error'])
                if 'op' in loaded_msg:
                    if loaded_msg['op'] in self.listeners:
                        self.listeners[loaded_msg['op']] = loaded_msg
                    await self.event_handler.handle(loaded_msg)
                if 'ref' in loaded_msg:
                    if loaded_msg['ref'] in self.listeners:
                        self.listeners[loaded_msg['ref']] = loaded_msg
                if 'fetchId' in loaded_msg:
                    if loaded_msg['fetchId'] in self.listeners:
                        self.listeners[loaded_msg['fetchId']] = loaded_msg
            else:
                await self.event_handler.run('on_pong')
