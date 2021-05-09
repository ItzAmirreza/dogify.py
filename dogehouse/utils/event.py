import asyncio
from ..core.User import User
from ..core.Room import Room
from .commands import handleCommand


class EventHandler:
    def __init__(self, event_listeners, commands_listeners, handlers, prefix):
        self.event_listeners = event_listeners
        self.commands_listeners = {
            "prefix": prefix,
            "listeners": commands_listeners
        }
        self.handlers = handlers

    async def handle(self, data):
        op = data['op']
        print("op --> ", op)

        if op == "auth:request:reply":
            # await self.handlers['auth'](data)
            pass
        elif op == "room:get_top:reply":
            pass
        elif op == "new-tokens":
            await self.run('__on_new_token', data['d'])
            await self.run('on_new_token', data['d'])
        elif op == "join_room_and_get_info:reply":
            pass
        elif op == "fetch_done":
            pass
        elif op == "active_speaker_change":
            pass
        elif op == "user_left_room":
            await self.run("on_user_leave", data["p"]["userId"])
        elif op == "new_user_join_room":
            await self.run('on_user_join', User(data["d"]["user"]))
        elif op == "mute_changed":
            pass
        elif op == "deafen_changed":
            pass
        elif op == "chat:send_msg:reply":
            pass
        elif op == "new_chat_msg":
            msg = handleCommand(
                data, self.commands_listeners.get('prefix'), self.commands_listeners.get('listeners'))
            self.run('on_new_message', msg)
        elif op == "message_deleted":
            pass
        elif op == "you-joined-as-pear":
            pass
        elif op == "you-joined-as-speaker":
            asyncio.ensure_future(self.handlers['connect_rtc'](data['d']))
        elif op == "leave_room:reply":
            pass
        elif op == "hand_raised":
            pass
        elif op == "speaker_added":
            pass
        elif op == "speaker_removed":
            pass
        elif op == "you-are-now-a-speaker":
            pass
        elif op == "room:set_role:reply":
            pass
        elif op == "room:set_active_speaker:reply":
            pass
        elif op == "room:create:reply":
            pass
        elif op == "user:create_bot:reply":
            pass

    async def run(self, event, *args, **kwargs):
        if event in self.event_listeners:
            func = self.event_listeners[event](*args, **kwargs)
            await asyncio.get_running_loop.create_task(func)
