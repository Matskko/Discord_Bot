import discord

intents = discord.Intents.default()
intents.message_content = True

client = discord.Client(intents=intents)

@client.event
async def on_ready():
    print(f'We have logged in as {client.user}')

@client.event
async def on_message(message):
    if message.author == client.user:
        return

    if message.content.startswith('$hello'):
        await message.channel.send('Hello!')

    if message.content.startswith('$goodbye'):
        await message.channel.send('Goodbye!')

    if message.content.startswith('$help'):
        await message.channel.send('How can I assist you?')

client.run('MTIyOTMzNzQ1MjY2NjI5MDI0Nw.GVm1DV.0jp_9tEjkWRrO4J70MxPB3ukk9SJJ7ySclWRMM')