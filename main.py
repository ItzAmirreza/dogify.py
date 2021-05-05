import datetime
import dogehouse
import asyncio

token = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJhdWQiOiJKb2tlbiIsImV4cCI6MTYyMDIyMjE2MywiaWF0IjoxNjIwMjE4NTYzLCJpc3MiOiJKb2tlbiIsImp0aSI6IjJwdTJvY285c2xrMTc3YWhwODAwZGhpMSIsIm5iZiI6MTYyMDIxODU2MywidXNlcklkIjoiYjYyZTU4M2ItMTVjNy00Nzk1LWFlMWMtNmQ1NzEzMGNiZjFiIn0.4SBOUpAgIukrgmxWE5ZD2fIEgbP7BNX9DBFy56GAsvU"
rtoken = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJhdWQiOiJKb2tlbiIsImV4cCI6MTYyMjgxMDU2MywiaWF0IjoxNjIwMjE4NTYzLCJpc3MiOiJKb2tlbiIsImp0aSI6IjJwdTJvY285dDE1NGo3YWhwODAwZGhqMSIsIm5iZiI6MTYyMDIxODU2MywidG9rZW5WZXJzaW9uIjoyLCJ1c2VySWQiOiJiNjJlNTgzYi0xNWM3LTQ3OTUtYWUxYy02ZDU3MTMwY2JmMWIifQ.9-xDmMHGRz0raxr86KFxweQ1vpFN27JX3Er0BFVDdB0"

client = dogehouse.Client(prefix='!')

@client.event
async def on_ready(ctx):
    print(f'started bot {ctx.displayName} with id {ctx.id}')
    # await client.joinRoom("b1aaf141-4aad-446c-9374-50356a9bba4a")
    await client.create_room('test','tst',isPrivate=True)
    

@client.event
async def on_message(msg):
    # print(msg.content)
    pass



@client.command
async def unmute(ctx):
    print('hoi!')

@client.command
async def mute(ctx):
    print('hoi!')

@client.command
async def stop(ctx):
    print('hoi!')

@client.command
async def play(ctx):
    print('hoi!')



client.run("77a42e92-7a48-43ae-9554-25bbaea3fda6")
