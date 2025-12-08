import asyncio
from discord.ext import commands
import random
import discord

class slots(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.symbols = ['🍒', '🍋', '🍊', '🍇', '🍉', '🔔', '💰', '🍀', '⭐', '🎲', '🎈', '🎁', '🏆', '🍓', '🍍', '🍎', '🍐', '🍋', '🍌', '🍫', '🍬', '🍭', '🍮', '🍯', '🍰', '🍱', '🍲', '🍳', '🍴', '🍵', '🍶', '🍷', '🍸', '🍹', '🍺', '🍻', '🥂', '🥃', '🥤', '🥢', '🥡', '🥧', '🥨', '🥩', '🥪', '🥫', '🥟', '🥠', '🥡', '🥥', '🥦', '🥨', '🥩', '🥪', '🥬', '🥯', '🧀', '🧁']
        self.players = {}

    def generate_slot_results(self):
        return [random.choice(self.symbols) for _ in range(3)]

    def calculate_payout(self, results):
        if len(set(results)) == 1:
            # All symbols are the same
            if results[0] == '💰':
                return 10
            elif results[0] == '🔔':
                return 5
            else:
                return 2
        elif len(set(results)) == 2:
            # Two symbols are the same
            return 1
        else:
            # No matching symbols
            return 0

    @commands.command(name='slots')
    async def slots(self, ctx: commands.Context):
        if ctx.author.id in self.players:
            await ctx.send("You're already playing slots!")
            return

        self.players[ctx.author.id] = True

        slot_embed = discord.Embed(
            title="Slot Machine",
            color=discord.Color.gold()
        )
        slot_embed.add_field(name="Instructions", value="Click 🎰 to spin the slot machine, or ⏹️ to stop playing.", inline=False)

        spin_button = discord.ui.Button(label="🎰", style=discord.ButtonStyle.primary)
        stop_button = discord.ui.Button(label="⏹️", style=discord.ButtonStyle.danger)

        view = discord.ui.View()
        view.add_item(spin_button)
        view.add_item(stop_button)

        slot_message = await ctx.send(embed=slot_embed, view=view)

        while True:
            try:
                interaction = await ctx.bot.wait_for("interaction", check=lambda i: i.message == slot_message, timeout=30)
                await interaction.response.defer()
                user_choice = interaction.data["custom_id"]
            except asyncio.TimeoutError:
                slot_embed.set_field_at(0, name="Instructions", value="You took too long to respond!", inline=False)
                await slot_message.edit(embed=slot_embed, view=None)
                break

            if user_choice == spin_button.custom_id:
                results = self.generate_slot_results()
                payout = self.calculate_payout(results)

                slot_embed = discord.Embed(
                    title="Slot Machine",
                    color=discord.Color.gold()
                )
                slot_embed.add_field(name="Results", value=' '.join(results), inline=False)

                if payout > 0:
                    slot_embed.add_field(name="Payout", value=f"You won {payout} credits!", inline=False)
                    slot_embed.set_footer(text="Congratulations! You won!")
                else:
                    slot_embed.add_field(name="Payout", value="No payout this time.", inline=False)
                    slot_embed.set_footer(text="Better luck next time!")

                await slot_message.edit(embed=slot_embed)
            elif user_choice == stop_button.custom_id:
                slot_embed.set_field_at(0, name="Game Over", value="Thank you for playing!", inline=False)
                slot_embed.set_field_at(1, name="", value="", inline=False)
                slot_embed.set_footer(text="Come back soon!")
                await slot_message.edit(embed=slot_embed, view=None)
                break

        del self.players[ctx.author.id]

def setup(bot):
    bot.add_cog(slots(bot))