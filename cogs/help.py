import os

import discord
from discord import app_commands
from discord.ext import commands

from dotenv import load_dotenv

load_dotenv(".env")
SERVER_ID = os.getenv("SERVER_ID")


class HelpCog(commands.Cog):
    def __init__(self, bot: commands.Bot) -> None:
        self.bot = bot

    @app_commands.command(
        name="introduce",
        description="Testing command"
    )
    async def introduce(self, interaction: discord.Interaction, name: str):
        print(f"Hello {name}")
        await interaction.response.send_message("Hello" + name)

    @commands.command(name="normal")
    async def normal(self, context: commands.Context):
        await context.send("Ok")


async def setup(bot: commands.Bot):
    await bot.add_cog(HelpCog(bot), guilds=[discord.Object(id=SERVER_ID), ])
