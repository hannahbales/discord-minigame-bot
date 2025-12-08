import asyncio
from discord.ext import commands
import random
import discord

class blackjack(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.players = {}
        self.deck = self.create_deck()
    
    def create_deck(self):
        card_categories = ['\u2665', '\u2666', '\u2660', '\u2663']  # hearts, diamond, spades, club
        cards_list = ['A', '2', '3', '4', '5', '6', '7', '8', '9', '10', 'J', 'Q', 'K']
        deck = [(category, card) for card in cards_list for category in card_categories]  # creates deck
        return deck
    
    def calculate_score(self, hand):
        score = sum(self.card_value(card) for card in hand)
        num_aces = sum(1 for card in hand if card[1] == 'A')
        ace_used = False

        #specify if dealt ace = 1 or 11
        for card in hand:
            if card[1] == 'A':
                if not ace_used:
                    ace_used = True
                else:
                    if score > 21:
                        score -= 10
                        num_aces -= 1
        return score
    
    def card_value(self, card):
        if card[1] in ['J', 'Q', 'K']:
            return 10
        elif card[1] == 'A':
            return 11
        else:
            return int(card[1])
    
    @commands.command(name = "blackjack")
    async def blackjack(self, ctx: commands.Context):
        if ctx.author.id in self.players:
            await ctx.send("You're already in a game!")
            return
        
        await ctx.send("Starting a new game of blackjack!")

        random.shuffle(self.deck)

        # deal hands
        self.players[ctx.author.id] = [self.deck.pop(), self.deck.pop()]
        bot_hand = [self.deck.pop(), self.deck.pop()]

        # calculate init scores
        player_score = self.calculate_score(self.players[ctx.author.id])
        bot_score = self.calculate_score(bot_hand)

        # embed message
        game_embed = discord.Embed(
            title = "Blackjack",
            color = discord.Color.red()
        )
        game_embed.add_field(name = f"{ctx.author.name}'s Hand      ", value = ' '.join(card[0] + card[1] for card in self.players[ctx.author.id]), inline = False)
        game_embed.add_field(name = "Bot's Hand         ", value = f"{bot_hand[1][0]}{bot_hand[1][1]}", inline=False)
        game_embed.add_field(name = "Current State" , value = "Hit or Stand?", inline = False)

        hit_button = discord.ui.Button(label = "Hit", style = discord.ButtonStyle.green)
        stand_button = discord.ui.Button(label = "Stand", style = discord.ButtonStyle.red)

        view = discord.ui.View()
        view.add_item(hit_button)
        view.add_item(stand_button)

        message = await ctx.send(embed = game_embed, view = view)

        while True:
            if player_score > 21:
                game_embed.set_field_at(2, name = "Current State", value = "You Busted!", inline = False)
                await message.edit(embed = game_embed, view = None)
                break
            
            try:
                interaction = await ctx.bot.wait_for("interaction", check = lambda i: i.message == message, timeout = 30)
                await interaction.response.defer()
                user_choice = interaction.data["custom_id"]
            except asyncio.TimeoutError:
                game_embed.set_field_at(2, name = "Current State", value = "You took too long to respond!", inline = False)
                await message.edit(embed = game_embed, view = None)
                break

            if user_choice == hit_button.custom_id:
                    # user hits
                    new_card = self.deck.pop()
                    self.players[ctx.author.id].append(new_card)
                    player_score = self.calculate_score(self.players[ctx.author.id])

                    game_embed.set_field_at(0, name = f"{ctx.author}'s Hand         ", value = ' '.join(card[0] + card[1] for card in self.players[ctx.author.id]), inline = False)
                    await message.edit(embed = game_embed, view = view)

            elif user_choice == stand_button.custom_id:
                    # user stands
                while bot_score < 17:
                    new_card = self.deck.pop()
                    bot_hand.append(new_card)
                    bot_score = self.calculate_score(bot_hand)
                    
                if bot_score > 21:
                        game_embed.set_field_at(2, name = "Current State", value = "Bot Busted! You win!", inline = False)
                elif bot_score > player_score:
                        game_embed.set_field_at(2, name = "Current State", value = "Bot wins!", inline = False)
                elif bot_score < player_score:
                        game_embed.set_field_at(2, name = "Current State", value = "You win!", inline = False)
                else:
                        game_embed.set_field_at(2, name = "Current State", value = "It's a tie!", inline = False)

                game_embed.set_field_at(1, name = "Bot's Hand", value = ' '.join(card[0] + card[1] for card in bot_hand[2:]), inline = False)
                await message.edit(embed = game_embed, view = None)
                break

        game_embed.set_field_at(0, name = f"{ctx.author}'s Score", value = player_score, inline = False)
        game_embed.set_field_at(1, name = "Bot's Score", value = bot_score, inline = False)
        await message.edit(embed = game_embed)

        del self.players[ctx.author.id]

def setup(bot):
    bot.add_cog(blackjack(bot))



