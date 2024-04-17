import discord
from bs4 import BeautifulSoup
import requests
from urllib.parse import quote_plus
from collections import Counter
from settings import DISCORD_API_SECRET

intents = discord.Intents.default()
intents.message_content = True
intents.reactions = True

client = discord.Client(intents=intents)

playing_games = []
vote_data = {}

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
        help_message = (
            "How can the great wizard assist you?\n"
            "1. To greet the wizard, say '$hello wizard'.\n"
            "2. To bid farewell to the wizard, say '$goodbye'.\n"
            "3. To get help from the wizard, say '$wizard help'.\n"
            "4. To initiate a vote, say '$vote <question>'.\n"
            "5. To add 3 games to the list, say '$addgames <game1>, <game2>, <game3>'.\n"
            "6. To display the list of games, say '$showgames'.\n"
            "7. To clear the list of games, say '$cleargames'.\n"
            "8. To get information about a game, say '$gameinfo <game>'.\n"
            "9. To reset votes and points, say '$resetvotes'.\n"
        )
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
            for game in games:
                game_name, game_id, game_url = await get_steam_game_info(game.strip())
                if game_name and game_id and game_url:
                    playing_games.append((game_name, game_id, game_url))
                    # Allow voting for added game
                    vote_data[game_name] = {'👍': 0, '👎': 0}
                    await message.channel.send(f"Game added to the list: {game_name} - {game_id} - {game_url}")
                else:
                    await message.channel.send(f"Could not find information for the game: {game.strip()}")
                    break
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
    elif message.content.startswith('$gameinfo'):
        game_name = message.content[len('$gameinfo'):].strip()
        game_name, game_id, game_url = await get_steam_game_info(game_name)
        if game_name and game_id and game_url:
            info_message = f"Game Name: {game_name}\nGame ID: {game_id}\nURL: {game_url}"
            await message.channel.send(info_message)
        else:
            await message.channel.send(f"Could not find information for the game: {game_name}")
    elif message.content == '$resetvotes':
        await reset_points()
        await message.channel.send('Votes and points have been reset.')

@client.event
async def on_reaction_add(reaction, user):
    if user == client.user:
        return

    if reaction.message.content.startswith("Vote:"):
        question = reaction.message.content[len("Vote: "):].strip()
        if question in vote_data:
            if str(reaction) in ['👍', '👎']:
                vote_data[question][str(reaction)] += 1
                # Implementing point system and ranking games
                await rank_games()

async def rank_games():
    game_points = Counter()
    total_games = len(playing_games)
    for question, votes in vote_data.items():
        for i, game in enumerate(playing_games):
            points = (votes['👍'] * (total_games - i)) + (votes['👎'] * (i + 1))
            game_points[game] += points

    ranked_games = game_points.most_common()
    ranked_games_text = "\n".join([f"{game[0]} - {game[1]} - {game[2]}: {points} points" for game, points in ranked_games])
    await client.get_channel(1229333409843904522).send(f"Ranked Games:\n{ranked_games_text}")

client.run(DISCORD_API_SECRET)
