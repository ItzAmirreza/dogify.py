import dogehouse

client = dogehouse.Client(prefix='!')


@client.event
async def on_ready(ctx):
    print(f'started bot {ctx.displayName} with id   {ctx.id}')
    client.data['welcome'] = "to Testing Area!"
    await client.joinRoom("c1dc3ff4-d659-406a-9cc8-15236fcafc15")


@client.command
async def ping(ctx):
    await client.sendMessage('pong!')

client.run("77a42e92-7a48-43ae-9554-25bbaea3fda6")
