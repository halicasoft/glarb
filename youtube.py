import asyncio
import discord
from discord.ext import commands
import yt_dlp


ytdlp_options = {
    'format': 'bestaudio/best',
    'noplaylist': True,
    'quiet': False,
    'extractor_args': {
        'youtube': {
            'skip': ['dash', 'hls']  # fall back to simpler formats
        }
    },
    'ignoreerrors': True,
}

voice_clients = {}
ytdl = yt_dlp.YoutubeDL(ytdlp_options)
ffmpeg_options = {
    'before_options': '-reconnect 1 -reconnect_streamed 1 -reconnect_delay_max 5',
    'options': '-vn'
    }

playlists = {
    "battle": "https://www.youtube.com/playlist?list=PLkYCZ4ZCoNzC2n1WeeGsneVq_t47KuTms",
    "exploring": "https://www.youtube.com/playlist?list=PLkYCZ4ZCoNzD4VBov0fkAzGLMyUmP-4KB"
}


class YTDLP(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.command()
    async def play(self, ctx, playlist_name: str):

        if not ctx.author.voice:
             await ctx.send("You need to be in a voice channel to play music.")
             return
        if playlist_name not in playlists:
            await ctx.send("Invalid playlist name. Glarb is currently configured for two playlists: 'battle' and 'exploring'. Attach one of them at the end of !play.")
            return

        url = playlists[playlist_name]

        #play next
        try:
            loop = asyncio.get_event_loop()
            data = await loop.run_in_executor(
                None, lambda: ytdl.extract_info(url, download=False)
            )

            if 'entries' in data:
                data = data['entries'][0]

            audio_url = data['url']

        except Exception as e:
            await ctx.send(f"An error occurred while trying to fetch the audio: {str(e)}")

        #join audio and play the music
        try:
            loop = asyncio.get_event_loop()
            voice_client = await ctx.author.voice.channel.connect()
            voice_clients[ctx.guild.id] = voice_client
            player = discord.FFmpegPCMAudio(audio_url, **ffmpeg_options)
            source = discord.PCMVolumeTransformer(player, volume=0.5)

            await ctx.send(f"Now playing: {data.get('title', 'Unknown')}")
            voice_clients[ctx.guild.id].play(
                    source,
                    after=lambda e: print(f"Player error: {e}") if e else None
                )
        except Exception as e:
            await ctx.send(f"An error occurred while trying to play the audio: {str(e)}")
 
    @commands.command(name="stop")
    async def stop(self, ctx):
        if ctx.guild.id in voice_clients:
            voice_clients[ctx.guild.id].stop()
            await voice_clients[ctx.guild.id].disconnect()
            del voice_clients[ctx.guild.id]

    # play command

    # stop command

        






async def setup(bot):
        # finally, adding the cog to the bot
    await bot.add_cog(YTDLP(bot=bot))