class OpCodes:
    def __init__(self) -> None:
        self.AUTH= "auth:request"
        self.AUTH_REPLY = "auth:request:reply"
        self.TOP_ROOMS= "room:get_top"
        self.NEW_TOKENS= "new-tokens"
        self.JOIN_ROOM= "join_room_and_get_info"
        self.FETCH_DONE= "fetch_done"
        self.ACTIVE_SPEAKER_CHANGE= "active_speaker_change"
        self.USER_LEFT_ROOM= "user_left_room"
        self.USER_JOIN_ROOM= "new_user_join_room"
        self.MUTE_CHANGED= "mute_changed"
        self.DEAFEN_CHANGED= "deafen_changed"
        self.SEND_CHAT_MSG= "chat:send_msg"
        self.NEW_CHAT_MSG= "new_chat_msg"
        self.MSG_DELETED= "message_deleted"
        self.JOINED_PEER= "you-joined-as-peer"
        self.JOINED_SPEAKER= "you-joined-as-speaker"
        self.LEFT_ROOM= "you_left_room"
        self.HAND_RAISED= "hand_raised"
        self.SPEAKER_ADDED= "speaker_added"
        self.SPEAKER_REMOVED= "speaker_removed"
        self.NOW_SPEAKER= "you-are-now-a-speaker"
        self.SET_ROLE= "room:set_role"
        self.SET_SPEAKING= "room:set_active_speaker"
        self.CREATE_ROOM= "room:create"
        self.CREATE_BOT= "user:create_bot"