import asyncio
from discord.ext import commands
import random
import discord

class guess(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.players = {}
    
    @commands.command(name = "guess")
    async def game(self, ctx: commands.Context):
        if ctx.author.id in self.players:
            await ctx.send("You're already in a game!")
            return
        
        await ctx.send("Starting a new game of guess the number!")

        self.players[ctx.author.id] = random.randint(1, 100)

        game_embed = discord.Embed(
            title = "Guess the Number",
            color = discord.Color.green(),
        )
        game_embed.add_field(name = "", value = "Guess a number between 1 and 100", inline = False)

        message = await ctx.send(embed = game_embed)

        def check(m):
            return m.author == ctx.author and m.channel == ctx.channel and m.content.isdigit()

        for i in range(8):
            game_embed.set_footer(text = f"You have {8 - i} guesses left!")
            await message.edit(embed = game_embed)

            try:

                user_reponse = await self.bot.wait_for("message", timeout=30, check=check)
                user_guess = int(user_reponse.content)
            except asyncio.TimeoutError:
                await ctx.send("You took too long to respond!")
                break
            
            if user_guess < self.players[ctx.author.id]:
                game_embed.set_field_at(0, name = "", value = "Guess higher!")
            elif user_guess > self.players[ctx.author.id]:
                game_embed.set_field_at(0, name = "", value = "Guess lower!")
            else:
                game_embed.set_field_at(0, name="", value="You guessed it right!")
                game_embed.set_footer(text="You Win!")
                await message.edit(embed=game_embed)
                await ctx.send("https://tenor.com/m5X7PZDxQqn.gif")
                break

        if user_guess != self.players[ctx.author.id]:
            game_embed.set_field_at(0, name="", value=f"The number was {self.players[ctx.author.id]}")
            game_embed.set_footer(text="Game Over!")

            await message.edit(embed = game_embed)
            await ctx.send("https://tenor.com/tcfucyoCDXg.gif")

        del self.players[ctx.author.id]

def setup(bot):
    bot.add_cog(guess(bot))



