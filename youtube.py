import asyncio
import time
from unittest import result
import discord
from discord.ext import commands
import yt_dlp
import random
from urllib.parse import urlparse


ytdlp_options = {
    "format": "bestaudio/best",
    "noplaylist": True,
    "quiet": False,
    "extractor_args": {"youtube": {"skip": ["dash", "hls"]}},
    "ignoreerrors": True,
    "extract_flat": True,
}

voice_clients = {}
ytdl = yt_dlp.YoutubeDL(ytdlp_options)
ffmpeg_options = {
    "before_options": "-reconnect 1 -reconnect_streamed 1 -reconnect_delay_max 5",
    "options": "-vn",
}

playlists = {
    "battle": "https://www.youtube.com/playlist?list=PLkYCZ4ZCoNzC2n1WeeGsneVq_t47KuTms",
    "exploring": "https://www.youtube.com/playlist?list=PLkYCZ4ZCoNzD4VBov0fkAzGLMyUmP-4KB",
    "dndj": "https://www.youtube.com/playlist?list=PLK040sS7yn2fe834OKaeFDMEehH6u8ZlB",
}


class YTDLP(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.queue = []
        self.looping = False
        self.queue_titles = []

    def is_valid_url(self, url):
        try:
            result = urlparse(url)
            return result.netloc in ("www.youtube.com", "youtube.com", "youtu.be")
        except Exception:
            return False

    def voice_check(self, ctx):
        if not ctx.author.voice:
            return (
                False,
                "Foolish tadpole, you need to be in a voice channel to play music.",
            )
        return True, None

    async def initialise_voice_client(self, ctx):
        if ctx.guild.id not in voice_clients:
            voice_client = await ctx.author.voice.channel.connect()
            voice_clients[ctx.guild.id] = voice_client

    async def check_empty_queue(self, ctx):
        await asyncio.sleep(30)
        if self.queue == [] and ctx.guild.id in voice_clients:
            if not voice_clients[ctx.guild.id].is_playing():
                await ctx.send(
                    "The playlist has been empty for a while, supplicant. I am returning to my pond."
                )
                await voice_clients[ctx.guild.id].disconnect()
                del voice_clients[ctx.guild.id]

    @commands.command()
    async def playlist(self, ctx, playlist_name: str):

        is_valid, error_message = self.voice_check(ctx)
        if not is_valid:
            await ctx.send(error_message)
            return

        if playlist_name not in playlists:
            await ctx.send(
                "Invalid playlist name, foolish pond scum. Glarb is currently configured for three playlists: 'battle', 'exploring', and 'dndj'. Attach one of them at the end of !playlist."
            )
            return

        url = playlists[playlist_name]
        loop = asyncio.get_event_loop()

        await self.initialise_voice_client(ctx)

        try:

            data = await loop.run_in_executor(
                None, lambda: ytdl.extract_info(url, download=False)
            )
            self.queue = [e for e in data["entries"] if e is not None]
            self.queue_titles = [e.get("title", "Unknown") for e in self.queue]
            entry = self.queue.pop(0)
            video_data = await loop.run_in_executor(
                None, lambda: ytdl.extract_info(entry["url"], download=False)
            )

            if video_data is None:
                await self.play_next(ctx)
                return

            entry["title"] = data.get("title", "Unknown")
            audio_url = video_data["url"]

        except Exception as e:
            await ctx.send(
                f"Despite the efforts of my greatest seers, an error occurred while trying to fetch the audio: {str(e)}"
            )
            await self.play_next(ctx)
            return

        # join audio and play the music
        try:
            if audio_url is None:
                await ctx.send(
                    "My augurs could not find a valid audio stream for this video. Moving on to the next one."
                )
                await self.play_next(ctx)
                return

            player = discord.FFmpegPCMAudio(audio_url, **ffmpeg_options)
            source = discord.PCMVolumeTransformer(player, volume=0.5)

            await ctx.send(f"Now playing: {video_data.get('title', 'Unknown')}")
            voice_clients[ctx.guild.id].play(
                source,
                after=lambda e: (print(f"Player error: {e}") if e else None)
                or asyncio.run_coroutine_threadsafe(self.play_next(ctx), loop),
            )

        except Exception as e:
            await ctx.send(
                f"Despite the toil of my finest augurs, an error occurred while trying to play the audio: {str(e)}"
            )

    async def play_next(self, ctx):

        if not self.queue:
            await ctx.send("The playlist has come to an end, my supplicant.")
            asyncio.ensure_future(self.check_empty_queue(ctx))
            return

        entry = self.queue.pop(0)
        if self.looping:
            self.queue.append(entry)

        try:
            loop = asyncio.get_event_loop()
            data = await loop.run_in_executor(
                None, lambda: ytdl.extract_info(entry["url"], download=False)
            )
            if data is None:
                await self.play_next(ctx)
                return

            audio_url = data["url"]
        except Exception as e:
            await ctx.send(f"Glarb could not divine the next track: {str(e)}")
            await self.play_next(ctx)
            return

        player = discord.FFmpegPCMAudio(audio_url, **ffmpeg_options)
        source = discord.PCMVolumeTransformer(player, volume=0.5)

        if not self.looping:
            await ctx.send(f"Now playing: {data.get('title', 'Unknown')}")
        else:
            await ctx.send(
                f"My choir of toads are looping the following track: {data.get('title', 'Unknown')}"
            )

        loop = asyncio.get_event_loop()
        voice_clients[ctx.guild.id].play(
            source,
            after=lambda e: (print(f"Player error: {e}") if e else None)
            or asyncio.run_coroutine_threadsafe(self.play_next(ctx), loop),
        )

    @commands.command(name="skip")
    async def skip(self, ctx):
        if ctx.guild.id in voice_clients and voice_clients[ctx.guild.id].is_playing():
            await ctx.send("Skipping to the next track.")
            voice_clients[ctx.guild.id].stop()
        else:
            await ctx.send("There is no track currently playing, insect.")

    @commands.command(name="loop")
    async def loop(self, ctx, video: str):
        if not self.is_valid_url(video):
            await ctx.send(
                "The provided URL is not a YouTube link, insect."
            )
            return
        is_valid, error_message = self.voice_check(ctx)
        if not is_valid:
            await ctx.send(error_message)
            return
        self.queue = [{"url": video}]
        self.looping = True
        await self.initialise_voice_client(ctx)
        await self.play_next(ctx)

    @commands.command(name="play")
    async def play(self, ctx, video: str):
        if not self.is_valid_url(video):
            await ctx.send(
                "The provided URL is not a YouTube link. What are you trying to pull, little fly?"
            )
            return
        is_valid, error_message = self.voice_check(ctx)
        if not is_valid:
            await ctx.send(error_message)
            return
        if ctx.guild.id in voice_clients and voice_clients[ctx.guild.id].is_playing():
            self.queue.append({"url": video})
            await ctx.send("The track has been added to the queue, my tadpole.")
            return
        self.queue = [{"url": video}]
        self.looping = False
        await self.initialise_voice_client(ctx)
        await self.play_next(ctx)

    @commands.command(name="stop")
    async def stop(self, ctx):
        if ctx.guild.id in voice_clients:
            self.queue = []
            self.looping = False
            voice_clients[ctx.guild.id].stop()
            await voice_clients[ctx.guild.id].disconnect()
            del voice_clients[ctx.guild.id]
            await ctx.send("Going back to my pond.")

    @commands.command(name="shuffle")
    async def shuffle(self, ctx):
        if not self.queue:
            await ctx.send("The playlist is currently empty, my tadpole.")
            return

        random.shuffle(self.queue)
        await ctx.send("The order of the playlist has been shuffled, my tadpole.")

    @commands.command(name="queue")
    async def show_queue(self, ctx):
        if not self.queue:
            await ctx.send("The playlist is currently empty, my tadpole.")
            return

        await ctx.send(
            "I am consulting the swirling mists in my orb to reveal the current queue."
        )
        queue_titles = []
        loop = asyncio.get_event_loop()
        for entry in self.queue:
            try:
                data = await loop.run_in_executor(
                    None,
                    lambda entry=entry: ytdl.extract_info(entry["url"], download=False),
                )
                title = data.get("title", "Unknown")
                queue_titles.append(title)
            except Exception as e:
                queue_titles.append("Unknown")

        queue_message = "**Current playlist:**\n" + "\n".join(
            f"{idx + 1}. {title}" for idx, title in enumerate(queue_titles)
        )
        await ctx.send(queue_message)

    # @commands.command(name="np")
    # async def now_playing(self, ctx):
    #     if ctx.guild.id in voice_clients and voice_clients[ctx.guild.id].is_playing():
    #         current_source = voice_clients[ctx.guild.id].source
    #         if isinstance(current_source, discord.PCMVolumeTransformer):
    #             title = current_source.original.title
    #             await ctx.send(f"Now playing: {title}")
    #         else:
    #             await ctx.send(
    #                 "I am currently playing a track, but I cannot divine its title."
    #             )
    #     else:
    #         await ctx.send("There is no track currently playing, insect.")

    @commands.command(name="pause")
    async def pause(self, ctx):
        if ctx.guild.id in voice_clients and voice_clients[ctx.guild.id].is_playing():
            voice_clients[ctx.guild.id].pause()
            await ctx.send("The music has been paused, my tadpole.")
        else:
            await ctx.send("There is no track currently playing, insect.")

    @commands.command(name="resume")
    async def resume(self, ctx):
        if ctx.guild.id in voice_clients and voice_clients[ctx.guild.id].is_paused():
            voice_clients[ctx.guild.id].resume()
            await ctx.send("The music has been resumed, my tadpole.")
        else:
            await ctx.send("There is no track currently paused, insect.")


async def cog_load(self):
    print(f"{self.__class__.__name__} loaded!")


async def cog_unload(self):
    print(f"{self.__class__.__name__} unloaded!")


async def setup(bot):
    # finally, adding the cog to the bot
    await bot.add_cog(YTDLP(bot=bot))
