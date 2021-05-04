import dogehouse
import asyncio

token = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJhdWQiOiJKb2tlbiIsImV4cCI6MTYyMDE1NDI3MCwiaWF0IjoxNjIwMTUwNjcwLCJpc3MiOiJKb2tlbiIsImp0aSI6IjJwdHVzc3FxZDUxZWp1Z2IzbzAwcDJ0MSIsIm5iZiI6MTYyMDE1MDY3MCwidXNlcklkIjoiYjYyZTU4M2ItMTVjNy00Nzk1LWFlMWMtNmQ1NzEzMGNiZjFiIn0.6brcY0XsZzItkPyX8jmGzMEEXYJR-ULazJ8N0Ofb83w"
rtoken = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJhdWQiOiJKb2tlbiIsImV4cCI6MTYyMjc0MjY3MCwiaWF0IjoxNjIwMTUwNjcwLCJpc3MiOiJKb2tlbiIsImp0aSI6IjJwdHVzc3FxZGZnNGR1Z2IzbzAwcDJ1MSIsIm5iZiI6MTYyMDE1MDY3MCwidG9rZW5WZXJzaW9uIjoyLCJ1c2VySWQiOiJiNjJlNTgzYi0xNWM3LTQ3OTUtYWUxYy02ZDU3MTMwY2JmMWIifQ.1XOnp6yC-UkQYw-sLlONyg03l4EbdwLzedgTKVIc3NM"

client = dogehouse.Client()

@client.event
async def on_ready(ctx):
    print(f'started bot {ctx.displayName} with id {ctx.id}')
    result =  await client.joinRoom('9faf5e37-feeb-4415-8eb5-405edae483ac', forceLeave=True)
    if result:
        print(f"joined {result.name}")
        await asyncio.sleep(20)
        await client.leaveRoom()
        print("left the room.")
    else:
        print("Failed to join the room")
    # await client.close()
    

@client.event
async def on_user_join(user):
    print( user.username,"just joined!")

@client.event
async def on_user_leave(user):
    print("user with Id ", user.username," just left!")

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



client.run(token, rtoken)
