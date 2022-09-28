# pylint: disable=assigning-non-slot
import os

import discord
from discord.ext import commands
from dotenv import load_dotenv

load_dotenv(".env")

TOKEN = os.getenv("BOT_TOKEN")
SERVER_ID = os.getenv("SERVER_ID")


class MyBot(commands.Bot):
    def __init__(self) -> None:
        intents = discord.Intents.default()
        intents.message_content = True
        super().__init__(command_prefix="$", intents=intents, )

        self.initial_extensions = [
            'cogs.help',
            'cogs.mangacog',
            # 'cogs.bar',
        ]

        self.synced = False

    async def setup_hook(self) -> None:

        # self.session = None
        for ext in self.initial_extensions:
            await self.load_extension(ext)
        await self.tree.sync(guild=discord.Object(id=SERVER_ID))

    async def on_ready(self):
        await self.wait_until_ready()
        print(f'Logged on as {self.user}!')

    async def close(self):
        await super().close()
        # await self.session.close()


bot = MyBot()

bot.run(TOKEN)
