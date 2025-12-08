import asyncio
import discord
from discord.ext import commands
import os
import random
from dotenv import load_dotenv

# load environment variable
load_dotenv()

# create bot instance
bot = commands.Bot(command_prefix= "!", intents = discord.Intents.all())
bot.remove_command("help")

cog_files = [
    f"cogs.{filename[:-3]}" for filename in os.listdir("./cogs/") if filename.endswith(".py")
]

for cogfile in cog_files:
    try:
        bot.load_extension(cogfile)
    except Exception as err:
        print(err)

# event handler for when bot is ready
@bot.event
async def on_ready():
    print(f'{bot.user} is ready and online!')

# command to say hello to bot
@bot.command(name = "hello", description = "Say hello to the bot!")
async def hello(ctx):
    await ctx.send("Hey!")

# command to display help and documentation
@bot.command()
async def help(ctx):
    embed = discord.Embed(
        title = "Help & Documentation",
        description = "The documentation for the discord bot created by Team 7!",
        color = discord.Color.purple(),
    )

    # Add minigame commands help
    embed.add_field(name = "Minigame Commands", value = "Here are some minigame commands:", inline = False)
    embed.add_field(name = "BlackJack", value = "start the game with !blackjack", inline = True)
    embed.add_field(name = "Guess The Number", value = "start the game with !guess", inline = True)
    embed.add_field(name = "Trivia", value = "start the game with !quiz", inline = True)
    embed.add_field(name = "Word Scramble", value = "start the game with !wordscramble <difficulty>", inline = True)

    await ctx.send(embed = embed)

bot.run(os.getenv('TOKEN'))