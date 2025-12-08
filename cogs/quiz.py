import asyncio
from discord.ext import commands
import random
import discord
import os
import requests
import html

class quiz(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.command(name="quiz", description="Starts a quiz game!")
    async def quiz(self, ctx):
        # Create a view to hold the difficulty buttons
        difficulty_view = discord.ui.View()
        difficulty_options = ["Easy", "Medium", "Hard"]
        for option in difficulty_options:
            button = discord.ui.Button(label=option, style=discord.ButtonStyle.primary)
            button.callback = lambda interaction, selected_difficulty=option.lower(): difficulty_view.stop() or setattr(difficulty_view, "selected_difficulty", selected_difficulty)
            difficulty_view.add_item(button)

        # Send the difficulty selection message and wait for user's response
        difficulty_message = await ctx.send("Please select the difficulty level:", view=difficulty_view)
        await difficulty_view.wait()
        if hasattr(difficulty_view, "selected_difficulty"):
            difficulty = difficulty_view.selected_difficulty
        else:
            difficulty = "easy"
        await difficulty_message.delete()

        # Create a view to hold the number of questions buttons
        num_questions_view = discord.ui.View()
        num_questions_options = [str(i) for i in range(1, 11)]
        for option in num_questions_options:
            button = discord.ui.Button(label=option, style=discord.ButtonStyle.primary)
            button.callback = lambda interaction, selected_num=int(option): num_questions_view.stop() or setattr(num_questions_view, "selected_num", selected_num)
            num_questions_view.add_item(button)

        # Send the number of questions selection message and wait for user's response
        num_questions_message = await ctx.send("Please select the number of questions:", view=num_questions_view)
        await num_questions_view.wait()
        if hasattr(num_questions_view, "selected_num"):
            num_questions = num_questions_view.selected_num
        else:
            num_questions = 5
        await num_questions_message.delete()

        # Set the API URL with the selected difficulty and number of questions
        api_url = f"https://opentdb.com/api.php?amount={num_questions}&difficulty={difficulty}&type=multiple"

        # Send a GET request to the API
        response = requests.get(api_url)
        data = response.json()

        # Extract the questions and answers from the API response
        questions = []
        for item in data["results"]:
            question = {
                "question": html.unescape(item["question"]),
                "choices": [html.unescape(choice) for choice in item["incorrect_answers"]] + [html.unescape(item["correct_answer"])],
                "answer": html.unescape(item["correct_answer"])
            }
            questions.append(question)

        # Shuffle the questions
        random.shuffle(questions)

        # Initialize the score
        score = 0

        # Start the quiz
        await ctx.send("Welcome to the quiz game! Please join a voice channel & Answer the following questions.")

        for i in range(len(questions)):
            question = questions[i]

            # Create the embed for the question
            embed = discord.Embed(title=f"Question {i+1}", description=question['question'], color=discord.Color.blue())

            # Create a view to hold the buttons
            view = discord.ui.View()

            # Shuffle the choices
            random.shuffle(question["choices"])

            # Create buttons for each answer choice
            for choice in question["choices"]:
                button = discord.ui.Button(label=choice, style=discord.ButtonStyle.primary, custom_id=choice)
                view.add_item(button)

            # Send the embed and the buttons
            message = await ctx.send(embed=embed, view=view)

            # Wait for the user's answer
            try:
                interaction = await ctx.bot.wait_for("interaction", check=lambda i: i.message == message and i.user == ctx.author, timeout=30)
                user_answer = interaction.data["custom_id"]

                # Display the user's answer
                await interaction.response.send_message(f"You selected: {user_answer}")

                # Check if the user's answer is correct
                if user_answer == question["answer"]:
                    await ctx.send("Correct!")
                    score += 1
                else:
                    await ctx.send(f"Incorrect. The correct answer is: {question['answer']}")

                # Check if the user is connected to a voice channel
                if ctx.author.voice is not None:
                    # Check if the bot is connected to a voice channel
                    if ctx.voice_client is None:
                        # Join the voice channel of the user
                        voice_channel = ctx.author.voice.channel
                        await voice_channel.connect()

                    # Play the appropriate audio based on the answer
                    if user_answer == question["answer"]:
                        # Play the "yippee-tbh.mp3" audio for a correct answer
                        source = discord.FFmpegOpusAudio("song/yippee-tbh.mp3")
                        ctx.voice_client.play(source)
                    else:
                        # Play the "engineer_no01.mp3" audio for an incorrect answer
                        source = discord.FFmpegOpusAudio("song/engineer_no01.mp3")
                        ctx.voice_client.play(source)

                # Disable the buttons after the user answers
                view.stop()

                # Wait for the audio to finish playing before moving to the next question
                while ctx.voice_client is not None and ctx.voice_client.is_playing():
                    await asyncio.sleep(1)

            except asyncio.TimeoutError:
                await ctx.send("Time's up! Moving on to the next question.")

        # Display the final score
        await ctx.send(f"\nQuiz completed! Your score is: {score}/{len(questions)}")

        # Check if the user got all the questions right
        if score == len(questions):
            await ctx.send("Congratulations! You got all the questions right! Here's a song for you:")

            # Check if the user is connected to a voice channel
            if ctx.author.voice is not None:
                # Check if the bot is already connected to a voice channel
                if ctx.voice_client is None:
                    # Join the voice channel of the user
                    voice_channel = ctx.author.voice.channel
                    await voice_channel.connect()

                # Play the song
                source = discord.FFmpegOpusAudio("song/kirbys-victory-dance.mp3")
                ctx.voice_client.play(source, after=lambda e: print(f"Finished playing: {e}"))

                # Wait for the song to finish playing
                while ctx.voice_client is not None and ctx.voice_client.is_playing():
                    await asyncio.sleep(1)

                # Disconnect from the voice channel
                await ctx.voice_client.disconnect()
            else:
                await ctx.send("You need to be in a voice channel to hear the victory song.")
                
def setup(bot):
    bot.add_cog(quiz(bot))