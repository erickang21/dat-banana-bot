import discord
from discord.ext import commands
import datetime
import sys
import asyncio
import os
import aiohttp
import json
import youtube_dl



YOUTUBE_DL_OPTIONS = {
    'format': 'bestaudio',
    'noplaylist': True,
    'nocheckcertificate': True,
    'ignoreerrors': False,
    'logtostderr': False,
    'quiet': True,
    'no_warnings': True,
    'default_search': 'auto'
}


ffmpeg_options = {
    'before_options': '-nostdin',
    'options': '-vn'
}


ytdl = youtube_dl.YoutubeDL(YOUTUBE_DL_OPTIONS)


class YTDLSource(discord.PCMVolumeTransformer):
    def __init__(self, source, *, data, volume=0.5):
        super().__init__(source, volume)

        self.data = data

        self.title = data.get('title')
        self.url = data.get('url')

    @classmethod
    async def from_url(cls, url, *, loop=None, stream=False):
        loop = loop or asyncio.get_event_loop()
        data = await loop.run_in_executor(None, lambda: ytdl.extract_info(url, download=not stream))

        if 'entries' in data:
            data = data['entries'][0]

        filename = data['url'] if stream else ytdl.prepare_filename(data)
        return cls(discord.FFmpegPCMAudio(filename, **ffmpeg_options), data=data)




class Music:
    def __init__(self, bot):
       self.bot = bot


    @commands.command()
    async def connect(self, ctx):
        '''Connects the bot to your current voice channel.'''
        if ctx.author.voice is None:
            return await ctx.send("Looks like you aren't connected to a voice channel yet! Where do I join?")
        if ctx.voice_client is None:
            await ctx.author.voice.channel.connect()
            await ctx.send(f"Successfully connected to Voice Channel **{ctx.author.voice.channel.name}**. :white_check_mark:")
        else:
            await ctx.voice_client.move_to(ctx.author.voice.channel)
            await ctx.send(f"Successfully connected to Voice Channel: **{ctx.author.voice.channel.name}**. :white_check_mark:")


    @commands.command()
    async def disconnect(self, ctx):
        '''Disconnects the bot to your current voice channel. Cya!'''
        if ctx.voice_client is None:
            await ctx.send("Looks like I'm not connected to a voice channel yet! Can't disconnect...:thinking:")
        else:
            await ctx.voice_client.disconnect()
            await ctx.send(f"Successfully disconnected from the voice channel. :white_check_mark:")

    @commands.command()
    async def play(self, ctx, *, url):
        """Search for a YouTube video to play, by name."""
        if ctx.voice_client is None:
            await ctx.author.voice.channel.connect()
        if ctx.author.voice is None:
            return await ctx.send("Looks like you aren't connected to a voice channel yet, and neither am I! Where do I join?")
        try:
            player = await YTDLSource.from_url(url, loop=self.bot.loop)
            ctx.voice_client.play(player, after=lambda e: print('Player error: %s' % e) if e else None)
            await ctx.send('Now playing: **{}**'.format(player.title))
        except:
            await ctx.send("Please enter a valid YouTube URL to play.")


    


def setup(bot):
    bot.add_cog(Music(bot))

