import discord
from settings import DISCORD_API_SECRET

intents = discord.Intents.default()
intents.message_content = True
intents.reactions = True

client = discord.Client(intents=intents)

playing_games = []

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
        help_message += "5. To add 3 games to the list, say '$playinggame <game1>, <game2>, <game3>'.\n"
        help_message += "6. To display the list of games, say '$showgames'.\n"
        help_message += "7. To clear the list of games, say '$cleargames'.\n"
        await message.channel.send(help_message)
    elif message.content.startswith('$vote'):
        question = message.content[len('$vote'):].strip()
        if question:
            vote_message = await message.channel.send(f"Vote: {question}")
            await vote_message.add_reaction('👍')
            await vote_message.add_reaction('👎')
        else:
            await message.channel.send("Please provide a question to vote on using '$vote <question>'.")
    elif message.content.startswith('$playinggame'):
        games = message.content[len('$playinggame'):].strip().split(',')
        if len(games) == 3:
            playing_games.extend(games)
            await message.channel.send("Games added to the list!")
        else:
            await message.channel.send("Please provide exactly 3 games separated by commas.")
    elif message.content == '$showgames':
        if playing_games:
            game_list = "\n".join(playing_games)
            await message.channel.send(f"List of games:\n{game_list}")
        else:
            await message.channel.send("No games added to the list yet.")
    elif message.content == '$cleargames':
        playing_games.clear()
        await message.channel.send("Games list cleared.")

@client.event
async def on_reaction_add(reaction, user):
    if user == client.user:
        return

    if reaction.message.content.startswith("Vote:"):
        # Here you can implement logic to handle reactions to vote messages
        pass

client.run(DISCORD_API_SECRET)
