import asyncio
import websockets
from websockets import exceptions as wserror
import functools
from .core.User import User
from .core.Room import Room
from .core.constants import constants
import json
import uuid

heartBeatInterval = constants['heartBeatInterval']
connectionTimeOut = constants['connectionTimeout']

__all__ = ("Client")

class Client():
    def __init__(self,prefix=""):
        super(Client, self).__init__()
        self.api = "wss://api.dogehouse.tv/socket"
        self.loop = asyncio.get_event_loop()
        
        self.prefix = prefix
        self.token = None
        self.client = None

        self.events = {}
        self.commands = {}

        self.ws = None
        self.cachedUsers = []
        self.cachedRooms = []

        self.currentRoom = None

        
        # starting authentication
        print("starting authentication")
        self._ready = asyncio.Event()

        

    def event(self, func):
        self.events[func.__name__] = func

    def command(self,func):
        self.commands[func.__name__] = func
    
    # async def close(self):
    #     self.loop.stop()
    #     self.loop.close()

    def run(self,token, refreshToken):
        try:
            if not isinstance(token, str):
                raise Exception("Invalid token")
            self.token = token

        except:
            raise Exception("Invalid token")
        finally:
            asyncio.ensure_future(self.authenticate(token, refreshToken))
            self.loop.run_forever()
        

    async def HeartBeat(self):
        await asyncio.sleep(heartBeatInterval/1000)
        await self.ws.ping()
        while True:
            await asyncio.sleep(heartBeatInterval/1000)
            await self.ws.ping()

    async def EventListeners(self):
        print(self.events)
        async for msg in self.ws:
            if not msg == 'pong':
                loadedJson = json.loads(msg)
                if loadedJson['op'] == "new_user_join_room" and "on_user_join" in self.events:
                    await self.events["on_user_join"](User(loadedJson["d"]["user"]))
                if loadedJson['op'] == "user_left_room" and "on_user_leave" in self.events:
                    await self.events["on_user_leave"](User(loadedJson["d"]["userId"]))
                

    async def getTopPublicRooms(self):

        fetchId = str(uuid.uuid4())
        data = {"op": "get_top_public_rooms", "d": {
            "cursor": 0}, "fetchId": fetchId}
        await self.ws.send(json.dumps(data))
        answer = json.loads(await self.ws.recv())
        if not answer["fetchId"] == fetchId:
            return None

        roomslist = []
        for room in answer["d"]["rooms"]:
            roomobj = Room(room)
            roomslist.append(roomobj)

        return roomslist

    

    async def joinRoom(self, roomId, forceLeave=False):
        if not self.currentRoom is None:
            if forceLeave:
                await self.leaveRoom()
            else:
                return False

        fetchId = str(uuid.uuid4())
        #{"op":"join_room_and_get_info","d":{"roomId":"bb7c1e4f-d364-415a-8a4d-db8e64a0fec5"},"fetchId":"b4283f25-a116-4838-a936-f1616c9b8360"}
        data = {"op":"join_room_and_get_info","d":{"roomId":roomId},"fetchId":fetchId}
        await self.ws.send(json.dumps(data))
        answer = ''
        async for msg in self.ws:
            try:
                msg = json.loads(msg)
                if msg["fetchId"] == fetchId:
                    answer = msg
                    break
            except:
                pass
        
        return Room(answer["d"]["room"])
    

    async def leaveRoom(self):
        if self.currentRoom is None:
            return True
        data ={"op":"leave_room","d":{}}
        await self.ws.send(json.dumps(data))
        return True
                
    

        
    async def authenticate(self, token, rtoken):

        self.ws = await websockets.connect(self.api)
            
            
        Adata = {
            "op": "auth",
            "d": {"accessToken": token, "refreshToken": rtoken,
                    "reconnectToVoice": True,
                    "currentRoomId": None,
                    "muted": False,
                    "deafened": False}
        }
        try:
            await self.ws.send(json.dumps(Adata))
            answer = json.loads(await self.ws.recv())
            if answer["op"] == "auth-good":
                self.client = User(answer["d"]["user"])
                #print(await self.getTopPublicRooms())
                eventListeners = self.loop.create_task(self.EventListeners())
                heartBeat =  self.loop.create_task(self.HeartBeat())
                ready = self.loop.create_task(self.events["on_ready"](self.client))
                if 'on_ready' in self.events:
                    await ready
                await asyncio.wait([heartBeat,eventListeners])
                
                    
                


            else:
                raise Exception(
                    "Could not have succesful authentication because of an unknown reason.")
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
    
            
            