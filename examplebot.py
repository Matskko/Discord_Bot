import discord
from settings import DISCORD_API_SECRET

intents = discord.Intents.default()
intents.message_content = True
intents.reactions = True

client = discord.Client(intents=intents)

playing_games = []

async def get_steam_game_info(game_name):
    search_query = quote_plus(game_name)
    url = f"https://store.steampowered.com/search/?term={search_query}"
    response = requests.get(url)
    soup = BeautifulSoup(response.text, 'html.parser')
    first_result = soup.find('a', class_='search_result_row')
    if first_result:
        game_id = first_result['data-ds-appid']
        game_url = first_result['href']
        return game_name, game_id, game_url
    else:
        return None, None, None

async def get_steam_game_info(game_name):
    search_query = quote_plus(game_name)
    url = f"https://store.steampowered.com/search/?term={search_query}"
    response = requests.get(url)
    soup = BeautifulSoup(response.text, 'html.parser')
    first_result = soup.find('a', class_='search_result_row')
    if first_result:
        game_id = first_result['data-ds-appid']
        game_url = first_result['href']
        return game_name, game_id, game_url
    else:
        return None, None, None

async def reset_points():
    global vote_data
    vote_data.clear()
    global playing_games
    playing_games = []

@client.event
async def on_ready():
    print(f'We have logged in as {client.user}')

@client.event
async def on_message(message):
    global playing_games

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
        help_message += "8. To show current votes, say '$showvotes'.\n"
        help_message += "9. To reset votes, say '$resetvotes'.\n"
        await message.channel.send(help_message)
    elif message.content.startswith('$vote'):
        question = message.content[len('$vote'):].strip()
        if question:
            vote_message = await message.channel.send(f"Vote: {question}")
            await vote_message.add_reaction('👍')
            await vote_message.add_reaction('👎')
            vote_data[question] = {'👍': 0, '👎': 0}
        else:
            await message.channel.send("Please provide a question to vote on using '$vote <question>'.")
    elif message.content.startswith('$addgames'):
        games = message.content[len('$addgames'):].strip().split(',')
        if len(games) == 3:
            playing_games.extend(games)
            await message.channel.send("Games added to the list!")
        else:
            await message.channel.send("Please provide exactly 3 games separated by commas.")
    elif message.content == '$showgames':
        if playing_games:
            game_list = "\n".join([f"{game[0]} - {game[1]} - {game[2]}" for game in playing_games])
            await message.channel.send(f"List of games:\n{game_list}")
        else:
            await message.channel.send("No games added to the list yet.")
    elif message.content == '$cleargames':
        playing_games.clear()
        await message.channel.send("Games list cleared.")
    elif message.content == '$showvotes':
        for question, votes in vote_data.items():
            await message.channel.send(f"{question}: 👍 {votes['👍']} | 👎 {votes['👎']}")
    elif message.content == '$resetvotes':
        vote_data.clear()
        await message.channel.send('Votes have been reset.')

@client.event
async def on_reaction_add(reaction, user):
    if user == client.user:
        return

    if reaction.message.content.startswith("Vote:"):
        question = reaction.message.content[len("Vote: "):].strip()
        if question in vote_data:
            if str(reaction) in ['👍', '👎']:
                vote_data[question][str(reaction)] += 1
            else:
                await reaction.message.channel.send("Invalid reaction.")

client.run(DISCORD_API_SECRET)
