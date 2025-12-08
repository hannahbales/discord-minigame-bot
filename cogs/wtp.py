import discord
from discord.ext import commands
import pokebase as pb
import random
import asyncio

class WhosThatPokemon(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.players = {}

    def generate_pokemon(self):
        pokemon_id = random.randint(1, 1025)
        pokemon = pb.pokemon(pokemon_id)
        return pokemon

    @commands.command(name='wtp')
    async def guess_pokemon(self, ctx: commands.Context):
        if ctx.author.id in self.players:
            await ctx.send("You're already playing Who's That Pokemon?")
            return

        self.players[ctx.author.id] = {"score": 0, "playing": False}

        poke_embed = discord.Embed(
            title="Who's That Pokemon?",
            description="Can you guess the Pokemon based on its sprite?",
            color=discord.Color.blue()
        )
        poke_embed.add_field(name="Instructions", value="Click the ▶️ button to begin! Type your answer in chat. When you answer correctly, the next pokemon will appear. If you answer incorrectly then the game ends.", inline=False)

        start_button = discord.ui.Button(label="▶️", style=discord.ButtonStyle.primary)
        
        view = discord.ui.View()
        view.add_item(start_button)

        poke_message = await ctx.send(embed=poke_embed, view=view)
        
        while True:
            try:
                interaction = await ctx.bot.wait_for('interaction', check=lambda i: i.message == poke_message, timeout=30)
                await interaction.response.defer()
                user_choice = interaction.custom_id
            except asyncio.TimeoutError:
                poke_embed.set_field_at(0, name="Instructions", value="You took too long to respond!", inline=False)
                await poke_message.edit(embed=poke_embed, view=None)
                break

            score = self.players[ctx.author.id]["score"]

            if user_choice == start_button.custom_id:
                poke_embed.clear_fields()
                pokemon = self.generate_pokemon()
                poke_embed.set_image(url=pokemon.sprites.front_default)
                poke_embed.set_footer(text=f"Score: {score}")
                view.remove_item(start_button)

                await poke_message.edit(embed=poke_embed, view=view)

                while True:
                    def check(m):
                        return m.author == ctx.author and m.channel == ctx.channel

                    try:
                        guess_msg = await ctx.bot.wait_for('message', check=check, timeout=30)
                        guess = guess_msg.content.lower()

                        if guess == pokemon.name.lower():
                            self.players[ctx.author.id]["score"] += 1
                            score = self.players[ctx.author.id]["score"]

                            pokemon = self.generate_pokemon()
                            poke_embed.set_image(url=pokemon.sprites.front_default)
                            poke_embed.set_footer(text=f"Score: {score}")
                            await poke_message.edit(embed=poke_embed, view=view)
                        else:
                            poke_embed = discord.Embed(
                                title="Who's That Pokemon?",
                                color=discord.Color.blue()
                            )
                            poke_embed.add_field(name="Game Over", value=f"Incorrect guess! The Pokemon was {pokemon.name}.", inline=False)
                            poke_embed.set_footer(text=f"Final Score: {score}")
                            await poke_message.edit(embed=poke_embed, view=None)
                            break

                    except asyncio.TimeoutError:
                        poke_embed = discord.Embed(
                            title="Who's That Pokemon?",
                            color=discord.Color.blue()
                        )
                        poke_embed.add_field(name="Game Over", value="You took too long to respond!", inline=False)
                        poke_embed.set_footer(text=f"Final Score: {score}")
                        await poke_message.edit(embed=poke_embed, view=None)
                        break
                    
            break

        del self.players[ctx.author.id]
        
def setup(bot):
    bot.add_cog(WhosThatPokemon(bot))