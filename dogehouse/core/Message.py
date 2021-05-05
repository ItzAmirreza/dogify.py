import datetime
from .User import User

class Message:
    def __init__(self, data):
        self.authorid = data["userId"]
        self.author = self.getUser(data)
        self.id = data["id"]
        self.isWhisper = data["isWhisper"]
        self.sentAt = datetime.datetime.strptime(
                f"{data['sentAt'].split('T')[0]} {data['sentAt'].split('T')[1].replace('Z', '')}", '%Y-%m-%d %H:%M:%S.%f')
        self.content = self.getContent(data["tokens"])

    def getUser(self, data):
        data["id"] = data["userId"]
        data["bannerUrl"] = None
        data["bio"] = None
        data["botOwnerId"] = None
        data["currentRoomId"] = None
        data["followsYou"] = None
        data["youAreFollowing"] = None
        data["lastOnline"] = str(datetime.datetime.now()).replace(" ", "T") + "Z"
        data["numFollowers"] = None
        data["numFollowing"] = None
        data["roomPermissions"] = None
        return User(data)


    def getContent(self, tokens):
        whole_message = ""
        count = 0
        for each in tokens:
            text = self.typeConvertor(each)
            if count == 0:
                whole_message = whole_message + text
                count += 1
            else:
                whole_message = whole_message + " " + text
        return whole_message

    
    def typeConvertor(self, token):
        if token["t"] == "emote":
            return ":" + token["v"] + ":"
        elif token["t"] == "mention":
            return "@" + token["v"]
        else:
            return token["v"]




