import asyncio
from discord.ext import commands
import random
import discord

class dice(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.players = {}
        
    @commands.command(name="dice")
    async def game(self, ctx: commands.Context, *, dice_spec: str = None):
        if ctx.author.id in self.players:
            await ctx.send("You're already in a game!")
            return
        
        if dice_spec is None:
            await ctx.send("Please provide the dice specification. Usage: !dice <numberofdice>d<sides of dice>")
            return
        
        try:
            num_dice, num_sides = dice_spec.split("d")
            num_dice = int(num_dice)
            num_sides = int(num_sides)
        except (ValueError, TypeError):
            await ctx.send("Invalid dice specification. Please use the format: !dice <numberofdice>d<sides of dice>")
            return
        
        if num_dice <= 0 or num_sides <= 0:
            await ctx.send("Number of dice and sides must be positive integers.")
            return
        
        await ctx.send(f"Starting a new game of dice roll with {num_dice} dice and {num_sides} sides each!")

        self.players[ctx.author.id] = [random.randint(1, num_sides) for _ in range(num_dice)]

        game_embed = discord.Embed(
            title="Dice Roll",
            color=discord.Color.blue(),
        )
        game_embed.add_field(name="", value=f"Guess the sum of the {num_dice} dice rolls (each with {num_sides} sides)", inline=False)

        message = await ctx.send(embed=game_embed)

        def check(m):
            return m.author == ctx.author and m.channel == ctx.channel and m.content.isdigit()

        timeout = False
        for i in range(7):
            game_embed.set_footer(text=f"You have {7 - i} guesses left!")
            await message.edit(embed=game_embed)

            try:
                user_response = await self.bot.wait_for("message", timeout=30, check=check)
                user_guess = int(user_response.content)
            except asyncio.TimeoutError:
                await ctx.send("You took too long to respond!")
                timeout = True
                break
            
            actual_sum = sum(self.players[ctx.author.id])
            if user_guess < actual_sum:
                game_embed.set_field_at(0, name="", value="The sum of the dice rolls is higher!")
            elif user_guess > actual_sum:
                game_embed.set_field_at(0, name="", value="The sum of the dice rolls is lower!")
            else:
                game_embed.set_field_at(0, name="", value="You guessed the sum of the dice rolls correctly!")
                game_embed.set_footer(text="You Win!")
                await message.edit(embed=game_embed)
                await ctx.send("https://media.tenor.com/_iuND6vkOsgAAAAi/win-best.gif")
                break
        
        if not timeout:
            if user_guess != actual_sum:
                game_embed.set_field_at(0, name="", value=f"The sum of the dice rolls was {actual_sum}")
                game_embed.set_footer(text="Game Over!")

                await message.edit(embed=game_embed)
                await ctx.send("https://media1.tenor.com/m/eTqdoJ96YP4AAAAd/failure-fail.gif")

        del self.players[ctx.author.id]
        
def setup(bot):
    bot.add_cog(dice(bot))

