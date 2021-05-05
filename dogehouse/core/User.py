import datetime


class User:
    def __init__(self, data):
        self.id = data["id"]
        self.username = data["username"]

        self.avatarUrl = data["avatarUrl"]
        self.bannerUrl = data["bannerUrl"]
        self.bio = data["bio"]
        self.botOwnerId = data["botOwnerId"]
        self.currentRoomId = data["currentRoomId"]
        self.displayName = data["displayName"]
        self.followers = data["followsYou"]
        self.following = data["youAreFollowing"]
        self.blockedUsers = data["iBlockedThem"]
        try:
            self.lastonlinedatetime = datetime.datetime.strptime(
                f"{data['lastOnline'].split('T')[0]} {data['lastOnline'].split('T')[1].replace('Z', '')}", '%Y-%m-%d %H:%M:%S.%f')
        except:
            self.lastonlinedatetime = None
        self.followersCount = data["numFollowers"]
        self.followingCount = data["numFollowing"]
        self.roomPermissions = data["roomPermissions"]

    async def update(self, data):
        self.id = data["id"]
        self.username = data["username"]

        self.avatarUrl = data["avatarUrl"]
        self.bannerUrl = data["bannerUrl"]
        self.bio = data["bio"]
        self.botOwnerId = data["botOwnerId"]
        self.currentRoomId = data["currentRoomId"]
        self.displayName = data["displayName"]
        self.followers = data["followsYou"]
        self.following = data["youAreFollowing"]
        self.blockedUsers = data["iBlockedThem"]
        try:
            self.lastonlinedatetime = datetime.datetime.strptime(
                f"{data['lastOnline'].split('T')[0]} {data['lastOnline'].split('T')[1].replace('Z', '')}", '%Y-%m-%d %H:%M:%S.%f')
        except:
            self.lastonlinedatetime = None
        self.followersCount = data["numFollowers"]
        self.followingCount = data["numFollowing"]
        self.roomPermissions = data["roomPermissions"]
