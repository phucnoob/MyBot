import os

import discord
from discord import app_commands
from discord.ext import tasks
from discord.ext import commands

from dotenv import load_dotenv
from manga.servers import Server  # pylint: disable=maybe-no-member
from manga.servers.nettruyen import Nettruyen

load_dotenv(".env")
SERVER_ID = os.getenv("SERVER_ID")


class MangaCog(commands.Cog):
    def __init__(self, bot: commands.Bot) -> None:
        self.bot = bot
        self.mangas_data = None
        self.server: Server = None

    async def cog_load(self):
        self.server: Server = Nettruyen()
        self.spamn.start()  # pylint: disable=maybe-no-member
        print("Manga cogs ok.")

    @tasks.loop(seconds=5)
    async def spamn(self):
        print("Me..")

    def make_embed(self, data: dict):
        embed = discord.Embed(
            title=data["name"], url=data["url"], description=data["status"], color=0x27ae60)
        embed.set_author(name=data["author"])
        embed.set_thumbnail(url=data["cover"])
        embed.set_footer(text=data["synopsis"])

        return embed

    @app_commands.command(
        name="next",
        description="Next result of last search."
    )
    async def next(self, interaction: discord.Interaction):
        await interaction.response.defer(ephemeral=True)
        await self.handle_next(interaction)

    @app_commands.command(
        name="search",
        description="Search for a manga name and return first result."
    )
    async def search(self, interaction: discord.Interaction, name: str):
        await interaction.response.defer(ephemeral=True)
        self.mangas_data = await self.server.search(name)
        await self.handle_next(interaction)

    async def handle_next(self, interaction: discord.Interaction):
        try:
            data = await self.mangas_data.pop().info
            embed = self.make_embed(data)
            await interaction.followup.send(embed=embed)
        except IndexError:
            await interaction.followup.send("Nothing found!")


async def setup(bot: commands.Bot):
    await bot.add_cog(MangaCog(bot), guilds=[discord.Object(id=SERVER_ID), ])
