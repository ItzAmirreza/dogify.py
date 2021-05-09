import datetime
import uuid
import json
import asyncio
import websockets
import aiohttp
from websockets import exceptions as wserror

from .core.constants import constants
from .core.User import User
from .core.Room import Room
from .core.operationCodes import OpCodes as oc
from .utils.gateway import Connection
from.utils.audio import AudioConnection
OpCodes = oc()


heartBeatInterval = constants['heartBeatInterval']
connectionTimeOut = constants['connectionTimeout']


__all__ = ("Client")


class Client():
    def __init__(self, prefix="", tick=.1, Uri="wss://api.dogehouse.tv/socket"):
        super(Client, self).__init__()
        self._uri = Uri
        self._tick = tick
        self._loop = asyncio.get_event_loop()
        self.data = {}
        self._prefix: str = prefix
        self._token: str = None
        self._rToken: str = None

        self._handlers = {
            'connect_rtc': self.connect_rtc,
            'connect-transport': self.connect_transport,
            'tracks': self.tracks,
            '__on_new_token': self.__on_new_token
        }
        self._events: dict = {}
        self._commands: dict = {}

        self.ws = None
        self._cachedUsers: list = []
        self._cachedRooms: list = []

        self._listeners: dict = {}
        self.currentRoom: Room = None

        self.audio_connection = AudioConnection(self._handlers)

    def event(self, func) -> None:
        self._events[func.__name__] = func

    async def __on_new_token(self, ctx) -> None:
        self.token = ctx['accessToken']
        self.rToken = ctx['refreshToken']
        # res = await self.auth()

    def command(self, func) -> None:
        self._commands[func.__name__] = func

    # async def close(self):
    #     self.loop.stop()
    #     self.loop.close()

    def run(self, apiKey) -> None:
        try:
            if not isinstance(apiKey, str):
                raise Exception("Invalid token")
            self.apiKey = apiKey
            asyncio.ensure_future(self.main())
            self._loop.run_forever()

        except KeyboardInterrupt:
            pass
        finally:
            self._loop.run_until_complete(self.audio_connection.close())

    async def main(self) -> None:
        self.connection = Connection(
            self._uri,
            self._events,
            self._commands,
            self._loop,
            self._handlers,
            self._prefix,
            self._tick, )
        await self.connection.initialize()
        await self.get_bot_tokens(self.apiKey)
        await self.auth()
        if 'on_ready' in self._events:
            ready = self._loop.create_task(
                self._events["on_ready"](self.client))
            await asyncio.wait([ready])

    async def connect_rtc(self, data):
        await self.audio_connection.init(data)
        await self.sendWs('speaking_change', {"value": True}, Legacy=True)

    async def connect_transport(self, data):
        await self.sendWs('@connect-transport', data, Legacy=True)

    async def catch(self, op):
        return await self.gateway.capture(op)

    async def tracks(self, type, data):
        if type == "send":
            await self.get('@send-track', data, True, True)
            return await self.waitFor('@send-track-send-done')
        else:
            await self.get('@get-recv-tracks', data, True, True)
            data = await self.waitFor('@get-recv-tracks-done')
            await self.audio_connection.consumeArr(data['d'])

    async def get_bot_tokens(self, apiKey):
        async with aiohttp.request("POST", "https://api.dogehouse.tv/bot/auth", headers={"Content-Type": "application/json"}, data=json.dumps({"apiKey": apiKey})) as res:
            res.raise_for_status()
            res = await res.json()
            self.token = res['accessToken']
            self.rToken = res['refreshToken']

    async def get(self, OpCode, Data, Legacy=False, NoRes=False):
        if NoRes:
            return await self.sendWs(OpCode, Data, Legacy=Legacy)
        else:
            return await self.waitFor(await self.sendWs(OpCode, Data, Legacy=Legacy))

    async def sendWs(self, OpCode, Data, ref=str(uuid.uuid4()), Legacy=False) -> str:
        if Legacy:
            await self.connection.send(json.dumps({"op": OpCode, "d": Data, "fetchId": ref}))
        else:
            await self.connection.send(json.dumps({"v": "0.2.0", "op": OpCode, "p": Data, "ref": ref}))
        return ref

    async def waitFor(self, ref):
        res = await self.connection.get(ref)
        return res

    async def getTopPublicRooms(self):
        res = await self.get(OpCodes.TOP_ROOMS, {"cursor": 0})
        roomslist = []
        for room in res["p"]["rooms"]:
            roomobj = Room(room)
            roomslist.append(roomobj)
        return roomslist

    async def joinRoom(self, roomId, forceLeave=False) -> Room:
        if not self.currentRoom is None:
            if forceLeave:
                await self.leaveRoom()
                self.currentRoom = None
            else:
                return False
        res = await self.get(OpCodes.JOIN_ROOM, {"roomId": roomId}, Legacy=True)
        roomobj = Room(res["d"]["room"])
        self.currentRoom = roomobj

        return roomobj

    async def leaveRoom(self):
        if self.currentRoom == None:
            return False
        await self.get(OpCodes.LEFT_ROOM, {}, Legacy=True)
        self.currentRoom = None
        return True

    async def sendMessage(self, message):
        if self.currentRoom:
            tokens = []
            wholemsg = message.split(" ")
            for each in wholemsg:
                type, each = await self.typeDetector(each)
                goingdata = {"t": type, "v": each}
                tokens.append(goingdata)
            await self.get(OpCodes.SEND_CHAT_MSG, {"tokens": tokens, "whisperedTo": []}, NoRes=True)
        else:
            raise Exception("You are not in a room.")

    async def typeDetector(self, text) -> str:
        roomusernames = []
        if text.startswith(":") and text.endswith(":"):
            return "emote", text.replace(":", "")
        elif text.startswith('@') and text in roomusernames:
            return "mention", text.replace("@", "")
        else:
            return "text", text

    async def defean(self):
        self.get(OpCodes.DEAFEN_CHANGED, {"deafened": True})

    async def undefean(self):
        fetchId = str(uuid.uuid4())
        data = {"v": "0.2.0", "op": "room:deafen",
                "p": {"deafened": False}, "ref": fetchId}
        await self.ws.send(json.dumps(data))

    async def schedule_room(self, name="not defined", description="not defined", time=datetime.datetime.now()):
        if not isinstance(time, datetime.datetime):
            raise Exception("Please put a valid datetime object")
        fetchId = str(uuid.uuid4())
        time = str(time).replace(" ", "T") + "Z"

        data = {"op": "schedule_room", "d": {"name": name, "scheduledFor": time,
                                             "description": description, "cohosts": []}, "fetchId": fetchId}
        res = await self.get("schedule_room", data, True)
        return res["d"]["scheduledRoom"]["id"]

    async def create_room(self, name, description="", isPrivate=False):

        if isPrivate:
            isPrivate = "private"
        else:
            isPrivate = "public"
        res = await self.get(OpCodes.CREATE_ROOM, {"name": name, "privacy": isPrivate, "description": description})
        firstdata = res["p"]
        firstdata["inserted_at"] = str(
            datetime.datetime.now()).replace(" ", "T") + "Z"
        firstdata["numPeopleInside"] = 1
        firstdata["peoplePreviewList"] = [self.client]
        firstdata["voiceServerId"] = None
        room = Room(firstdata)
        self.currentRoom = room
        return room

    async def auth(self):
        data = {
            "accessToken": self.token,
            "refreshToken": self.rToken,
            "deafened": False,
            "muted": False,
            "reconnectToVoice": False,
        }
        try:
            await self.get(OpCodes.AUTH, data, NoRes=True)
            print('waiting..')
            res = await self.waitFor('auth:request:reply')
            print('got it! --> ', res)
            self.client = User(res["p"])
        except wserror.ConnectionClosedError as ex:
            if ex.code == 4001:
                raise Exception("Invalid authentication")
            elif ex.code == 4003:
                raise Exception(
                    "Connection closed by server. (Multi connection with 1 token is forbidden)")
            elif ex.code == 1006:
                raise Exception(
                    "Connection timeout. (Something is wrong with your network or their network?)")
            else:
                raise Exception(ex)
        except Exception as ex:
            print(ex)
