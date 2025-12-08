import asyncio
import discord
from discord.ext import commands
from discord import ui
import random

class ConnectFour(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.command(name="connectfour", description="Starts Connect Four")
    async def connect_four(self, ctx):
        self.ctx = ctx
        self.board = [[":white_circle:" for _ in range(7)] for _ in range(6)]
        self.players = ["🔴", "🔵"]
        self.current_player = 0
        self.winner = None

        await self.start()

    async def start(self):
        embed = discord.Embed(
            title="Connect Four Game",
            description="Welcome to Connect Four! Players take turns dropping their colored discs into the grid. The first player to get four of their discs in a row (horizontally, vertically, or diagonally) wins!",
            color=discord.Color.blue()
        )
        await self.ctx.send(embed=embed)
        await asyncio.sleep(3)

        await self.play_turn()

    async def play_turn(self):
        embed = discord.Embed(
            title="Connect Four",
            description=f"Current Player: {self.players[self.current_player]}",
            color=discord.Color.blue()
        )
        embed.add_field(name="Board", value=self.format_board(), inline=False)

        view = ui.View()
        for i in range(7):
            button = ui.Button(label=str(i+1), style=discord.ButtonStyle.primary, custom_id=str(i+1))
            button.callback = self.handle_button_click
            view.add_item(button)

        message = await self.ctx.send(embed=embed, view=view)

    async def handle_button_click(self, interaction):
        column = int(interaction.data["custom_id"]) - 1
        if self.is_valid_move(column):
            row = self.get_next_open_row(column)
            self.board[row][column] = self.players[self.current_player]
            if self.is_winner(row, column):
                self.winner = self.players[self.current_player]
                await interaction.response.edit_message(embed=self.create_embed(), view=None)
                await self.ctx.send(f"Player {self.winner} wins!")
                return
            self.current_player = (self.current_player + 1) % 2
            await interaction.response.edit_message(embed=self.create_embed())
        else:
            await interaction.response.send_message("Invalid move! Please try again.", ephemeral=True)

    def format_board(self):
        return "\n".join(["".join(row) for row in self.board])

    def is_valid_move(self, column):
        return self.board[0][column] == ":white_circle:"

    def get_next_open_row(self, column):
        for row in range(5, -1, -1):
            if self.board[row][column] == ":white_circle:":
                return row

    def is_winner(self, row, column):
        return (
            self.check_horizontal(row, column) or
            self.check_vertical(row, column) or
            self.check_diagonal_up(row, column) or
            self.check_diagonal_down(row, column)
        )

    def check_horizontal(self, row, column):
        color = self.board[row][column]
        count = 0
        for c in range(7):
            if self.board[row][c] == color:
                count += 1
                if count == 4:
                    return True
            else:
                count = 0
        return False

    def check_vertical(self, row, column):
        color = self.board[row][column]
        count = 0
        for r in range(6):
            if self.board[r][column] == color:
                count += 1
                if count == 4:
                    return True
            else:
                count = 0
        return False

    def check_diagonal_up(self, row, column):
        color = self.board[row][column]
        count = 0
        r, c = row, column
        while r > 0 and c > 0:
            r -= 1
            c -= 1
        while r < 6 and c < 7:
            if self.board[r][c] == color:
                count += 1
                if count == 4:
                    return True
            else:
                count = 0
            r += 1
            c += 1
        return False

    def check_diagonal_down(self, row, column):
        color = self.board[row][column]
        count = 0
        r, c = row, column
        while r < 5 and c > 0:
            r += 1
            c -= 1
        while r >= 0 and c < 7:
            if self.board[r][c] == color:
                count += 1
                if count == 4:
                    return True
            else:
                count = 0
            r -= 1
            c += 1
        return False

    def create_embed(self):
        embed = discord.Embed(
            title="Connect Four",
            description=f"Current Player: {self.players[self.current_player]}",
            color=discord.Color.blue()
        )
        embed.add_field(name="Board", value=self.format_board(), inline=False)
        return embed
    
def setup(bot):
    bot.add_cog(ConnectFour(bot))