import asyncio
import os
from collections import deque
from urllib.parse import urlparse

import discord
from discord import FFmpegPCMAudio, app_commands
from discord.ext import commands
from dotenv import load_dotenv
from pytube import YouTube, Search

load_dotenv(".env")
SERVER_ID = os.getenv("SERVER_ID")

FFMPEG_OPTIONS = {
    'before_options': '-reconnect 1 -reconnect_streamed 1 -reconnect_delay_max 5', 'options': '-vn'}


class YoutubeCog(commands.Cog):
    def __init__(self, bot: commands.Bot) -> None:
        self.bot = bot
        self.queue = deque()
        self.player = None
        self.current_song = None

    @app_commands.command(
        name="stop",
        description="Leave voice server."
    )
    async def stop(self, interaction: discord.Interaction):
        voice_client = discord.utils.get(
            self.bot.voice_clients, guild=interaction.guild)

        if voice_client is not None:
            await voice_client.disconnect()
            await interaction.response.send_message("Bot left.")
        else:
            await interaction.response.send_message("Not in any chanel.")

    @app_commands.command(
        name="pause",
        description="Pause current playing song."
    )
    async def pause(self, interaction: discord.Interaction):
        if self.player is None:
            return
        self.player.pause()
        await interaction.response.send_message(f"Pause {self.current_song.title}")

    @app_commands.command(
        name="resume",
        description="Resume current playing song."
    )
    async def resume(self, interaction: discord.Interaction):
        self.player.resume()
        await interaction.response.send_message(f"Resume {self.current_song.title}")

    @app_commands.command(
        name="skip",
        description="Skip current song."
    )
    async def skip(self, interaction: discord.Interaction):
        print("skip")
        # self.player._player.after = None
        skiped_song = self.current_song.title
        self.player.stop()
        await interaction.response.defer()
        await interaction.followup.send(f"Skip {skiped_song}")
        # await self.handle_play(interaction)

    @app_commands.command(
        name="list",
        description="List current songs in the queue."
    )
    async def list(self, interaction: discord.Interaction):
        MAX_LIST = 10
        count = 0
        description = ""
        for song in self.queue:
            count += 1
            description += f"{count}. {song.title}\n\n"
            if count > MAX_LIST:
                break
        description = "No song in queue" if description == "" else description
        embed = discord.Embed(color=0x3498db, description=description)
        await interaction.response.send_message(embed=embed)

    @app_commands.command(
        name="play",
        description="Play youtube music"
    )
    @app_commands.describe(
        url_or_query="youtube url or query"
    )
    async def play(self, interaction: discord.Interaction, url_or_query: str):
        if interaction.user.voice:
            await interaction.response.defer()
            y_tube = await self.async_wrapper(lambda: self.get_youtube_object(url_or_query))
            title = await self.async_wrapper(lambda: y_tube.title)

            self.queue.append(y_tube)
            if self.player is not None and self.player.is_playing():
                await interaction.followup.send(f"Add {title} to queue.")
                await interaction.followup.send(f"{len(self.queue)} songs in the queue.")
            else:
                await self.handle_play(interaction)
        else:
            await interaction.response.send_message("Please join a voice chanel.")

    @app_commands.command(
        name="thumbnail",
        description="Get thumnail of youtube video"
    )
    async def thumnail(self, interaction: discord.Interaction, url: str):
        await interaction.response.defer()
        yt_video = YouTube(url)
        await interaction.channel.send(yt_video.title)
        await interaction.channel.send(yt_video.thumbnail_url)

    async def _join(self, interaction: discord.Interaction):
        chanel = interaction.user.voice.channel

        voice = discord.utils.get(
            interaction.guild.voice_channels, name=chanel.name)
        voice_client = discord.utils.get(
            self.bot.voice_clients, guild=interaction.guild)

        if voice_client is None:
            voice_client = await voice.connect()
        else:
            await voice_client.move_to(chanel)

        self.player = voice_client
        return voice_client

    async def handle_play(self, interaction: discord.Interaction):
        print("handle_play")
        yt = self.queue.popleft()

        await interaction.followup.send("Currently playing...")
        await interaction.followup.send(yt.watch_url)
        if yt is None:
            return
        self.current_song = yt  # backup metadata

        loop = asyncio.get_event_loop()
        voice_client = await self._join(interaction)
        audio_link = await loop.run_in_executor(None, lambda: yt.streams.get_audio_only().url)
        audio_obj = FFmpegPCMAudio(
            executable="ffmpeg", source=audio_link, **FFMPEG_OPTIONS)

        voice_client.play(
            audio_obj,
            after=lambda e: asyncio.run_coroutine_threadsafe(self.handle_play(interaction), loop))

    def is_url(self, url) -> bool:
        url_obj = urlparse(url)
        return url_obj.scheme in ['http', 'https']

    async def async_wrapper(self, func):
        return await self.bot.loop.run_in_executor(None, func)

    def get_youtube_object(self, url_or_query: str) -> YouTube:
        return YouTube(url_or_query) if self.is_url(url_or_query) else Search(url_or_query).results[0]


async def setup(bot: commands.Bot):
    await bot.add_cog(YoutubeCog(bot))
