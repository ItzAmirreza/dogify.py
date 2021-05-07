import datetime
import dogehouse
import asyncio

client = dogehouse.Client(prefix='!')

usersinroom = {

}
#1
#{"op":"@connect-transport","d":{"transportId":"7bbcd0df-bd88-4b22-bb1b-b185a5287f56","dtlsParameters":{"role":"server","fingerprints":[{"algorithm":"sha-256","value":"99:63:54:EB:2E:15:17:55:E1:68:27:03:1E:F4:06:EA:72:D8:4B:70:CA:95:8D:46:1F:97:4F:F8:DC:7D:A9:3B"}]},"direction":"send"}}
#2
#{"op":"@send-track","d":{"transportId":"7bbcd0df-bd88-4b22-bb1b-b185a5287f56","kind":"audio","rtpParameters":{"codecs":[{"mimeType":"audio/opus","payloadType":111,"clockRate":48000,"channels":2,"parameters":{"minptime":10,"useinbandfec":1},"rtcpFeedback":[{"parameter":"","type":"transport-cc"}]}],"headerExtensions":[{"uri":"urn:ietf:params:rtp-hdrext:sdes:mid","id":4,"encrypt":false,"parameters":{}},{"uri":"http://www.webrtc.org/experiments/rtp-hdrext/abs-send-time","id":2,"encrypt":false,"parameters":{}},{"uri":"http://www.ietf.org/id/draft-holmer-rmcat-transport-wide-cc-extensions-01","id":3,"encrypt":false,"parameters":{}},{"uri":"urn:ietf:params:rtp-hdrext:ssrc-audio-level","id":1,"encrypt":false,"parameters":{}}],"encodings":[{"ssrc":3258397611,"dtx":false}],"rtcp":{"cname":"YUGLSjEpOQeaZR3y","reducedSize":true},"mid":"0"},"rtpCapabilities":{"codecs":[{"mimeType":"audio/opus","kind":"audio","preferredPayloadType":100,"clockRate":48000,"channels":2,"parameters":{"minptime":10,"useinbandfec":1},"rtcpFeedback":[{"parameter":"","type":"transport-cc"}]}],"headerExtensions":[{"kind":"audio","uri":"urn:ietf:params:rtp-hdrext:sdes:mid","preferredId":1,"preferredEncrypt":false,"direction":"sendrecv"},{"kind":"video","uri":"urn:ietf:params:rtp-hdrext:sdes:mid","preferredId":1,"preferredEncrypt":false,"direction":"sendrecv"},{"kind":"audio","uri":"http://www.webrtc.org/experiments/rtp-hdrext/abs-send-time","preferredId":4,"preferredEncrypt":false,"direction":"sendrecv"},{"kind":"video","uri":"http://www.webrtc.org/experiments/rtp-hdrext/abs-send-time","preferredId":4,"preferredEncrypt":false,"direction":"sendrecv"},{"kind":"video","uri":"http://www.ietf.org/id/draft-holmer-rmcat-transport-wide-cc-extensions-01","preferredId":5,"preferredEncrypt":false,"direction":"sendrecv"},{"kind":"audio","uri":"urn:ietf:params:rtp-hdrext:ssrc-audio-level","preferredId":10,"preferredEncrypt":false,"direction":"sendrecv"},{"kind":"video","uri":"urn:3gpp:video-orientation","preferredId":11,"preferredEncrypt":false,"direction":"sendrecv"},{"kind":"video","uri":"urn:ietf:params:rtp-hdrext:toffset","preferredId":12,"preferredEncrypt":false,"direction":"sendrecv"}]},"paused":false,"appData":{"mediaTag":"cam-audio"},"direction":"send"}}





@client.event
async def on_ready(ctx):
    print(f'started bot {ctx.displayName} with id   {ctx.id}')
    client.data['welcome'] = "to Testing Area!"
    await client.joinRoom("a7b144a1-2364-4020-add4-04e5428411d7")
    #room = await client.create_room('tst',isPrivate=True)
    #print(room.id)

    # await client.leaveRoom()
    # list = await client.getTopPublicRooms()
    # for each in list:
    #     print(each.name)


@client.event
async def on_message(msg):
    pass


@client.event
async def on_user_join(user):

    await client.sendMessage(f'Welcome @{user.username} ' + client.data['welcome'])


@client.command
async def ping(ctx):
    await client.sendMessage('pong!')


@client.command
async def set_context(ctx):
    if ctx.author.username == "Amirreza" or ctx.author.username == "VelterZi":
        client.data['welcome'] = ctx.content.replace(
            ctx.content.split(" ")[0] + " ", "")
        await client.sendMessage('Changed Welcome Text!')
    else:
        await client.sendMessage(" :ppOverheat: Sorry, you can't do that!  :F: ")


@client.command
async def help(ctx):
    await client.sendMessage(f"Welcome {client.data['welcome']}")
    await asyncio.sleep(1)
    await client.sendMessage("This Bot's Library is being Developed By @Amirreza & @VelterZi")
    await asyncio.sleep(1)
    await client.sendMessage("commands:")
    await asyncio.sleep(1)
    await client.sendMessage("!ping -- pong's back")
    await asyncio.sleep(1)
    await client.sendMessage("!set_context <txt> -- sets the welcome text")


client.run("77a42e92-7a48-43ae-9554-25bbaea3fda6")
