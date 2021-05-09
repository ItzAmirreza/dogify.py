from ..core.Message import Message


async def handleCommand(data, prefix, commands):
    MessageObj = Message(data['d']['msg'])
    if await hasPrefix(MessageObj):
        args = MessageObj.content.split(' ')
        command = args[0].replace(prefix, '')
        if command in commands:
            await commands[command](MessageObj)
    return MessageObj


async def hasPrefix(prefix: str, MessageObj: Message):
    if not prefix == '':
        if MessageObj.content.startswith(prefix):
            return True
        return False
    else:
        return True
