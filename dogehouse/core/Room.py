import datetime
from .User import User
import asyncio



class Room:
    def __init__(self, data):
        self.id = data["id"]
        self.name = data["name"]
        self.ownerId = data["creatorId"]
        self.description = data["description"]
        try:
            self.inserted_at = datetime.datetime.strptime(
                f"{data['inserted_at'].split('T')[0]} {data['inserted_at'].split('T')[1].replace('Z', '')}", '%Y-%m-%d %H:%M:%S.%f')
        except:
            self.inserted_at = None
        self.isPrivate = data["isPrivate"]
        self.usersCount = data["numPeopleInside"]
        try:
            self.users = self.usersList(data["peoplePreviewList"])
        except:
            try:
                self.users = data["peoplePreviewList"]
            except Exception as e:
                print(e)

        self.voiceServerId = data["voiceServerId"]

    def usersList(self, data):
        finallist = []
        for i in data:
            userdata = {
                "id": i["id"],
                "displayName": i["displayName"],
                "avatarUrl": i["avatarUrl"],
                "numFollowers": i["numFollowers"],
                "username": None,
                "bannerUrl": None,
                "bio": None,
                "botOwnerId": None,
                "currentRoomId": None,
                "followsYou": None,
                "youAreFollowing": None,
                "iBlockedThem": None,
                "lastOnline": None,
                "followingCount": None,
                "roomPermissions": None,
                "numFollowing": None
            }
            user = User(userdata)
            finallist.append(user)
        return finallist
    

        
