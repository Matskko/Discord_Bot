import discord
from bs4 import BeautifulSoup
import requests
from urllib.parse import quote_plus
from settings import DISCORD_API_SECRET

# Initialize Discord client
intents = discord.Intents.default()
intents.message_content = True
intents.reactions = True
client = discord.Client(intents=intents)

# Global variables
playing_games = []

# Helper functions

async def get_steam_game_info(game_name):
    """Retrieve information about a game from the Steam store."""
    search_query = quote_plus(game_name)
    url = f"https://store.steampowered.com/search/?term={search_query}"
    try:
        response = requests.get(url)
        response.raise_for_status()  # Raise HTTPError for bad status codes
        soup = BeautifulSoup(response.text, 'html.parser')
        first_result = soup.find('a', class_='search_result_row')
        if first_result:
            game_id = first_result['data-ds-appid']
            game_url = first_result['href']
            return game_name, game_id, game_url
        else:
            return None, None, None
    except Exception as e:
        print(f"Error fetching game information: {e}")
        return None, None, None

async def reset_games():
    """Reset playing games list."""
    global playing_games
    playing_games = []

# Discord event handlers

@client.event
async def on_ready():
    """Print a message when the bot is ready."""
    print(f'We have logged in as {client.user}')

@client.event
async def on_message(message):
    """Handle messages sent by users."""
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
            "4. To add 3 games to the list, say '$addgames <game1>, <game2>, <game3>'.\n"
            "5. To display the list of games, say '$showgames'.\n"
            "6. To clear the list of games, say '$cleargames'.\n"
            "7. To get information about a game, say '$gameinfo <game>'.\n"
            "8. To reset games list, say '$resetgames'.\n"
            "9. To start a poll for games, say '$startpoll'.\n"
        )
        await message.channel.send(help_message)
    elif message.content.startswith('$addgames'):
        games = message.content[len('$addgames'):].strip().split(',')
        if len(games) == 3:
            for game in games:
                game_name, game_id, game_url = await get_steam_game_info(game.strip())
                if game_name and game_id and game_url:
                    playing_games.append((game_name, game_id, game_url))
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
    elif message.content == '$resetgames':
        await reset_games()
        await message.channel.send('Games list has been reset.')
    elif message.content == '$startpoll':
        if playing_games:
            options = "\n".join([f"{index + 1}. {game[0]}" for index, game in enumerate(playing_games)])
            poll_message = f"React to vote for your favorite game:\n{options}"
            poll = await message.channel.send(poll_message)
            for index in range(len(playing_games)):
                emoji = f"{index + 1}\N{VARIATION SELECTOR-16}\N{COMBINING ENCLOSING KEYCAP}"
                await poll.add_reaction(emoji)  # Adding reactions 1️⃣, 2️⃣, 3️⃣, ..., 🔟, ...
        else:
            await message.channel.send("No games added to start a poll.")

@client.event
async def on_reaction_add(reaction, user):
    """Handle reaction adds."""
    if user == client.user:
        return
    if reaction.message.content.startswith("React to vote for your favorite game:"):
        selected_option = ord(reaction.emoji) - 0x31 if ord(reaction.emoji) <= 0x39 else ord(reaction.emoji) - 0x1F1E6 + 0x30 - 0x31
        if 0 <= selected_option < len(playing_games):
            selected_game = playing_games[selected_option][0]
            await reaction.message.channel.send(f"{user.name} voted for {selected_game}")
        else:
            await reaction.message.channel.send("Invalid option.")

# Run the bot
client.run(DISCORD_API_SECRET)
