import discord
from discord.ext import commands
import random
import asyncio

class wordscramble(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.word_bank_easy = ["apple", "banana", "orange", "grape", "lemon", "peach", "pear", "kiwi", "plum", "melon",
                               "dog", "cat", "bird", "fish", "rat", "frog", "duck", "bear", "lion", "tiger"]
        self.word_bank_medium = ["strawberry", "pineapple", "blueberry", "watermelon", "raspberry", "blackberry", "pomegranate",
                                 "apricot", "avocado", "cantaloupe", "elephant", "giraffe", "zebra", "rhinoceros", "hippopotamus",
                                 "crocodile", "alligator", "octopus", "elephant", "kangaroo"]
        self.word_bank_hard = ["chrysanthemum", "eccentricity", "mnemonic", "onomatopoeia", "paraphernalia", "pharmaceutical",
                               "philanthropy", "psychedelic", "quintessential", "telekinesis", "juxtaposition", "antidisestablishmentarianism",
                               "photosynthesis", "supercalifragilisticexpialidocious", "sesquipedalian", "serendipity", "palindrome",
                               "circumlocution", "perpendicular", "indubitably"]
        self.players = {}

    # function to scramble a word
    def scramble_word(self, word):
        scrambled_word = list(word)
        random.shuffle(scrambled_word)
        return ''.join(scrambled_word)

    # method to generate a new word
    def generate_new_word(self, ctx: commands.Context, view: discord.ui.View):
        difficulty = self.players[ctx.author.id]["difficulty"]
        if difficulty == "easy":
            word = random.choice(self.word_bank_easy)
        elif difficulty == "medium":
            word = random.choice(self.word_bank_medium)
        elif difficulty == "hard":
            word = random.choice(self.word_bank_hard)

        scrambled_word = self.scramble_word(word)

        game_embed = discord.Embed(
            title=f"{ctx.author.name}'s Game of Word Scramble:",
            color=discord.Color.blurple()
        )
        game_embed.add_field(name="Unscramble the word:", value=scrambled_word, inline=False)

        hint_button = discord.ui.Button(label="Hint?", style=discord.ButtonStyle.blurple, custom_id="hint_button")
        quit_button = discord.ui.Button(label="Quit", style=discord.ButtonStyle.red, custom_id="quit_button")

        view.clear_items()  # Clear existing buttons
        view.add_item(hint_button)
        view.add_item(quit_button)
        view.add_item(discord.ui.Button(label="New Word", style=discord.ButtonStyle.green, custom_id="new_word_button"))

        return word, game_embed

    # command to start the word scramble game
    @commands.command(name="wordscramble")
    async def wordscramble(self, ctx: commands.Context, difficulty: str = "easy"):
        if ctx.author.id in self.players:
            await ctx.send("You're already in a game!")
            return

        # Add the user to the players dictionary
        self.players[ctx.author.id] = {"score": 0, "difficulty": difficulty}

        # Select a word from the appropriate word bank based on difficulty
        if difficulty.lower() == "easy":
            word = random.choice(self.word_bank_easy)
        elif difficulty.lower() == "medium":
            word = random.choice(self.word_bank_medium)
        elif difficulty.lower() == "hard":
            word = random.choice(self.word_bank_hard)
        else:
            await ctx.send("Invalid difficulty level. Please choose 'easy', 'medium', or 'hard'.")
            return

        scrambled_word = self.scramble_word(word)

        game_embed = discord.Embed(
            title=f"{ctx.author.name}'s Game of Word Scramble:",
            color=discord.Color.blurple()
        )
        game_embed.add_field(name="Unscramble the word:", value=scrambled_word, inline=False)

        hint_button = discord.ui.Button(label="Hint?", style=discord.ButtonStyle.blurple, custom_id="hint_button")
        quit_button = discord.ui.Button(label="Quit", style=discord.ButtonStyle.red, custom_id="quit_button")

        view = discord.ui.View()
        view.add_item(hint_button)
        view.add_item(quit_button)
        view.add_item(discord.ui.Button(label="New Word", style=discord.ButtonStyle.green, custom_id="new_word_button"))

        message = await ctx.send(embed=game_embed, view=view)

        while True:
            try:
                # Wait for either user's message or button interaction
                user_guess_task = asyncio.create_task(self.bot.wait_for("message", check=lambda message: message.author == ctx.author, timeout=45))
                interaction_task = asyncio.create_task(self.bot.wait_for("interaction", check=lambda i: i.message == message, timeout=30))

                done, pending = await asyncio.wait([user_guess_task, interaction_task], return_when=asyncio.FIRST_COMPLETED)

                # Handle user's guess
                if user_guess_task in done:
                    user_guess = user_guess_task.result()
                    if user_guess.content.lower() == word:
                        self.players[ctx.author.id]["score"] += 1
                        game_embed.set_field_at(0, name="Correct!", value="You unscrambled the word.")
                        game_embed.add_field(name="Your Score:", value=self.players[ctx.author.id]["score"], inline=False)
                        await message.edit(embed=game_embed, view=view)
                    else:
                        game_embed.set_field_at(0, name="Incorrect!", value=f"The correct word was `{word}`.")
                        game_embed.add_field(name="Your Score:", value=self.players[ctx.author.id]["score"], inline=False)
                        await message.edit(embed=game_embed, view=view)

                # Handle button interaction for hint or new word
                if interaction_task in done:
                    interaction = interaction_task.result()
                    user_choice = interaction.data["custom_id"]
                    if user_choice == "hint_button":
                        hint_index = random.randint(0, len(word) - 1)
                        hint_str = "_" * hint_index + word[hint_index] + "_" * (len(word) - hint_index - 1)

                        game_embed.add_field(name=" ", value=f"Here's a hint: `{hint_str}`", inline=False)
                        await interaction.response.edit_message(embed=game_embed, view=view)
                        game_embed.remove_field(1)  # Remove the hint field after it's been displayed

                    elif user_choice == "quit_button":
                        del self.players[ctx.author.id]
                        await ctx.send("You have quit the game.")
                        await message.delete()
                        return

                    elif user_choice == "new_word_button":
                        word, game_embed = self.generate_new_word(ctx, view)
                        message = await ctx.send(embed=game_embed, view=view)

            except asyncio.TimeoutError:
                game_embed.clear_fields() 
                game_embed.add_field(name="Oops!!", value="Time's up!", inline=False)
                await message.edit(embed=game_embed, view=None)
                break

        # Remove the user from the players dictionary after the game ends
        del self.players[ctx.author.id]
        return

    # quit command
    @commands.command(name="quit")
    async def quit_game(self, ctx: commands.Context):
        if ctx.author.id in self.players:
            del self.players[ctx.author.id]
            await ctx.send("You have quit the game.")
        else:
            await ctx.send("You're not currently in a game.")

# register the cog with the bot
def setup(bot):
    bot.add_cog(wordscramble(bot))
