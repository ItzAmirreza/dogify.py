import datetime,uuid,json,asyncio,websockets,aiohttp
from websockets import exceptions as wserror
from .core.constants import constants
from .core.User import User
from .core.Room import Room
from .core.operationCodes import OpCodes as oc
from .utils.gateway import gateway
from.utils.audio import AudioConnection
OpCodes = oc()


heartBeatInterval = constants['heartBeatInterval']
connectionTimeOut = constants['connectionTimeout']


__all__ = ("Client")


class Client():
    def __init__(self, prefix="", tick=.1):
        super(Client, self).__init__()
        self.api = "wss://api.dogehouse.tv/socket"
        self.__tick = tick
        self.loop = asyncio.get_event_loop()

        self.rtc_connection = None
        self.data = {}
        self.prefix: str = prefix
        self.token: str = None
        self.rToken: str = None
        self.client: User = None

        self._ready = asyncio.Event()
        self._handlers = {
            'ready': self._handle_ready,
            'auth': self.confirm_auth,
            'connect_rtc': self.connect_rtc,
        }
        self._events: dict = {}
        self._commands: dict = {}

        self.ws = None
        self._cachedUsers: list = []
        self._cachedRooms: list = []

        self._listeners: dict = {}
        self.currentRoom: Room = None

        self._events['__on_new_token'] = self.__on_new_token
        # starting authentication
        self._ready = asyncio.Event()

    async def _handle_ready(self):
        self._ready.set()

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

        except:
            raise Exception("Invalid token")
        finally:
            asyncio.ensure_future(self.main())
            self.loop.run_forever()

    async def main(self) -> None:
        self.ws = await websockets.connect(self.api)
        await self.get_bot_tokens(self.apiKey)
        await self.auth()
        self.gateway = gateway(self.ws, self.loop, self._events, self.prefix,
                               self._commands, self.__tick, self._handlers, self.client)
        # eventListener = self.loop.create_task(self.EventListeners())
        await self._ready.wait()
        ready = self.loop.create_task(self._events["on_ready"](self.client))
        await asyncio.wait([ready])

    async def connect_rtc(self,data):
        print('connecting with WebRTC')
        self.rtc_connection = AudioConnection(data)
        await self.rtc_connection.init()
        await self.rtc_connection.run()

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
            await self.ws.send(json.dumps({"op": OpCode, "d": Data, "fetchId": ref}))
        else:
            await self.ws.send(json.dumps({"v": "0.2.0", "op": OpCode, "p": Data, "ref": ref}))
        return ref

    async def waitFor(self, ref):
        res = await self.gateway.get(ref)
        return res

    async def create_bot(self) -> None:
        # fetchId = str(uuid.uuid4())
        # raw = {"v":"0.2.0", "op":"user:create_bot","p":{"username": "Jonny"}, "ref":fetchId }
        # await self.ws.send(json.dumps(raw))
        # {"apiKey": "77a42e92-7a48-43ae-9554-25bbaea3fda6"}
        # res = await self.gateway.get(fetchId)
        pass

    async def getTopPublicRooms(self):

        #fetchId = str(uuid.uuid4())
        # data = {"op": "get_top_public_rooms", "d": , "fetchId": fetchId}
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
        print('joined Room:', roomId)
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
        await self.ws.send(json.dumps(data))
        res = await self.gateway.get(fetchId)
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
            await self.sendWs(OpCodes.AUTH, data)
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

    async def confirm_auth(self, authData):
        self.client = User(authData["p"])
        await self._handlers['ready']()
