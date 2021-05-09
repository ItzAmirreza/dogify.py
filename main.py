import dogehouse

client = dogehouse.Client(prefix='!')


@client.event
async def on_ready(ctx):
    print(f'started bot {ctx.displayName} with id   {ctx.id}')
    client.data['welcome'] = "to Testing Area!"
    await client.joinRoom("d4469568-367e-4632-acba-e7fa4dc2bcce")


@client.command
async def ping(ctx):
    await client.sendMessage('pong!')

client.run("77a42e92-7a48-43ae-9554-25bbaea3fda6")
