import discord

# Local imports
from settings import DISCORD_API_SECRET

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
    elif message.content.startswith('$goodbye'):
        await message.channel.send('Goodbye!')

    if message.content.startswith('$help'):
        await message.channel.send('How can I assist you?')

client.run(DISCORD_API_SECRET)