import asyncio
import discord
from discord.ext import commands
from discord import ui
import random

class Simon(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.command(name="simon", description="Starts Simon")
    async def simon(self, ctx):
        self.ctx = ctx
        self.sequence = []
        self.user_sequence = []
        self.round = 1
        self.colors = ["🔴", "🟢", "🟡", "🔵"]
        self.buttons = [
            ui.Button(emoji="🔴", style=discord.ButtonStyle.gray, custom_id="🔴"),
            ui.Button(emoji="🟢", style=discord.ButtonStyle.gray, custom_id="🟢"),
            ui.Button(emoji="🟡", style=discord.ButtonStyle.gray, custom_id="🟡"),
            ui.Button(emoji="🔵", style=discord.ButtonStyle.gray, custom_id="🔵")
        ]
        await self.start()

    async def start(self):
        embed = discord.Embed(
            title="Simon Game",
            description="Welcome to the Simon game! The bot will display a sequence of colors. Your task is to remember and repeat the sequence correctly.",
            color=discord.Color.blue()
        )
        await self.ctx.send(embed=embed)
        await asyncio.sleep(3)
        await self.play_round()

    async def play_round(self):
        self.sequence.append(random.choice(self.colors))
        self.user_sequence = []

        embed = discord.Embed(
            title=f"Round {self.round}",
            description="Watch the sequence carefully!",
            color=discord.Color.blue()
        )
        message = await self.ctx.send(embed=embed)

        for i, color in enumerate(self.sequence):
            await message.edit(content=f"Next color ({i+1}/{len(self.sequence)}):") # Display "Next color" message
            await asyncio.sleep(0.5)
            await message.edit(content=color)
            await asyncio.sleep(3)

        view = ui.View(timeout=10)
        for button in self.buttons:
            button.callback = self.handle_button_click
            view.add_item(button)
        await message.edit(content="Your turn!", view=view)

    async def handle_button_click(self, interaction):
        clicked_emoji = interaction.data["custom_id"]
        self.user_sequence.append(clicked_emoji)

        if len(self.user_sequence) <= len(self.sequence):
            # Check if the user's sequence matches the round sequence up to the current point
            if self.user_sequence != self.sequence[:len(self.user_sequence)]:
                await interaction.response.send_message("Wrong sequence! Game over.")
                self.sequence = []
                self.user_sequence = []
                self.round = 1
                return

        if len(self.user_sequence) < len(self.sequence):
            # User hasn't finished the sequence yet
            await interaction.response.defer()  # Acknowledge the interaction
            return

        if self.user_sequence == self.sequence:
            await interaction.response.send_message("Correct sequence! Moving to the next round.")
            self.round += 1
            await asyncio.sleep(2)
            await self.play_round()
        else:
            await interaction.response.send_message("Wrong sequence! Game over.")
            self.sequence = []
            self.user_sequence = []
            self.round = 1

def setup(bot):
    bot.add_cog(Simon(bot))