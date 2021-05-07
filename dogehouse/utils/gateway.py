import websockets
import asyncio
import json
from ..core.User import User
import datetime
from ..core.constants import constants
from ..core.Message import Message
from ..core.Room import Room
from ..core.operationCodes import OpCodes as oc
OpCodes = oc()


heartBeatInterval = constants['heartBeatInterval']


class gateway:
    def __init__(self, ws, loop: asyncio.get_event_loop, events: dict, prefix, commands, eventTick, handlers, client):
        self.tick = eventTick
        self.listeners = {}
        self.handlers = handlers
        self.prefix = prefix
        self.loop = loop
        self.client = client
        self.ws = ws
        self.commands = commands
        self.events = events
        self.loop.create_task(self.initLoop())
        # self.loop.run(initLoop)

    async def initLoop(self):
        asyncio.ensure_future(self._eventLoop())
        asyncio.ensure_future(self.HeartBeat())

    async def HeartBeat(self):
        await asyncio.sleep(heartBeatInterval/1000)
        await self.ws.ping()
        while True:
            await asyncio.sleep(heartBeatInterval/1000)
            await self.ws.ping()

    async def recieve(self, fetchId,):
        self.listeners[fetchId] = None
        while True:
            await asyncio.sleep(self.tick)
            if not self.listeners[fetchId] == None:
                res = self.listeners[fetchId]
                self.listeners.pop(fetchId)
                return res

    async def get(self, fetchId):
        res = self.loop.create_task(self.recieve(fetchId))
        return await res

    async def hasPrefix(self, MessageObj):
        if not self.prefix == '':
            if MessageObj.content.startswith(self.prefix):
                return True
            return False
        else:
            return True

    async def handleCommand(self, msgObj):
        print(msgObj.content)
        if await self.hasPrefix(msgObj):
            args = msgObj.content.split(' ')
            command = args[0].replace(self.prefix, '')
            print('has prefix!', command, self.commands)
            if command in self.commands:
                print('yes!')
                await self.commands[command](msgObj)

    async def run(self, event, *args, **kwargs):
        if event in self.events:
            func = self.events[event](*args, **kwargs)
            await self.loop.create_task(func)

    async def _eventLoop(self):

        async def auth_reply(self, loadedJson):
            await self.handlers['auth'](loadedJson)

        async def two():
            pass

        async def new_token(self, loadedJson):
            print(loadedJson)
            await self.run('__on_new_token', loadedJson['d'])
            await self.run('on_new_token', loadedJson['d'])

        async def four():
            pass

        async def five():
            pass

        async def six():
            pass

        async def seven(self, loadedJson):
            await self.run("on_user_leave", loadedJson["p"]["userId"])

        async def user_join_room(self, loadedJson):
            await self.run('on_user_join', User(loadedJson["d"]["user"]))

        async def nine():
            pass

        async def ten():
            pass

        async def eleven():
            pass

        async def twelve(self, loadedJson):
            MessageObj = Message(loadedJson['d']['msg'])
            await self.handleCommand(MessageObj)
            await self.run('on_message', MessageObj)

        async def thirteen():
            pass

        async def joined_as_pear(self,loadedJson):
            await self.handlers['connect_rtc'](loadedJson['d'])

        async def joined_as_speaker(self,loadedJson):
            await self.handlers['connect_rtc'](loadedJson['d'])

        async def sixteen():
            pass

        async def seventeen():
            pass

        async def eighteen():
            pass

        async def nineteen():
            pass

        async def twenty():
            pass

        async def twenty_one():
            pass

        async def twenty_two():
            pass

        async def twenty_three(self, loadedJson):
            firstdata = loadedJson['p']
            firstdata["inserted_at"] = str(
                datetime.datetime.now()).replace(" ", "T") + "Z"
            firstdata["numPeopleInside"] = 1
            firstdata["peoplePreviewList"] = [self.client]
            firstdata["voiceServerId"] = None
            room = Room(firstdata)
            await self.run('on_create_room', room)

        async def twenty_four():
            pass
        options = {
            OpCodes.AUTH_REPLY: auth_reply,
            # OpCodes.TOP_ROOMS + ":reply": two,
            OpCodes.NEW_TOKENS: new_token,
            # OpCodes.JOIN_ROOM + ":reply": four,
            # OpCodes.FETCH_DONE + ":reply": five,
            # OpCodes.ACTIVE_SPEAKER_CHANGE + ":reply": six,
            # OpCodes.USER_LEFT_ROOM + ":reply": seven,
            OpCodes.USER_JOIN_ROOM: user_join_room,
            # OpCodes.MUTE_CHANGED + ":reply": nine,
            # OpCodes.DEAFEN_CHANGED + ":reply": ten,
            # OpCodes.SEND_CHAT_MSG + ":reply": eleven,
            OpCodes.NEW_CHAT_MSG: twelve,
            # OpCodes.MSG_DELETED + ":reply": thirteen,
            OpCodes.JOINED_PEER: joined_as_pear,
            OpCodes.JOINED_SPEAKER: joined_as_speaker,
            # OpCodes.LEFT_ROOM + ":reply": sixteen,
            # OpCodes.HAND_RAISED + ":reply": seventeen,
            # OpCodes.SPEAKER_ADDED + ":reply": eighteen,
            # OpCodes.SPEAKER_REMOVED + ":reply": nineteen,
            # OpCodes.NOW_SPEAKER + ":reply": twenty,
            # OpCodes.SET_ROLE + ":reply": twenty_one,
            # OpCodes.SET_SPEAKING + ":reply": twenty_two,
            # OpCodes.CREATE_ROOM + ":reply": twenty_three,
            # OpCodes.CREATE_BOT + ":reply": twenty_four,

        }
        async for msg in self.ws:

            if not msg == 'pong':
                loadedJson = json.loads(msg)
                if 'op' in loadedJson:
                    op = loadedJson['op']
                    print("op:", op)
                    if op in options:
                        await options[op](self, loadedJson)
                    await self.run('on_socket_recieve', msg)
                if 'error' in loadedJson.get('d','p'):
                    raise Exception(loadedJson['d']['error'])

                if 'ref' in loadedJson:
                    if loadedJson['ref'] in self.listeners:
                        self.listeners[loadedJson['ref']] = loadedJson
                if 'fetchId' in loadedJson:
                    if loadedJson['fetchId'] in self.listeners:
                        self.listeners[loadedJson['fetchId']] = loadedJson
                