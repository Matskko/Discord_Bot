import discord
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

    if message.content.startswith('$hello wizard'):
        await message.channel.send('Hello!')
    elif message.content.startswith('$goodbye'):
        await message.channel.send('Goodbye!')
    elif message.content.startswith('$wizard help'):
        help_message = "How can the great wizard assist you?\n"
        help_message += "1. To greet the wizard, say '$hello wizard'.\n"
        help_message += "2. To bid farewell to the wizard, say '$goodbye'.\n"
        help_message += "3. To get help from the wizard, say '$wizard help'.\n"
        help_message += "4. To initiate a vote, say '$vote <question>'.\n"
        await message.channel.send(help_message)
    elif message.content.startswith('$vote'):
        question = message.content[len('$vote'):].strip()
        if question:
            vote_message = await message.channel.send(f"Vote: {question}")
            await vote_message.add_reaction('👍')
            await vote_message.add_reaction('👎')
        else:
            await message.channel.send("Please provide a question to vote on using '$vote <question>'.")
    elif message.content == '$':
        await message.channel.send('Sorry, I do not understand that command.')

client.run(DISCORD_API_SECRET)
