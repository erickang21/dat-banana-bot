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
            return await ctx.send("Looks like you aren't connected to a voice channel yet! Where do I join?")
        await ctx.trigger_typing()
        try:            
            player = await YTDLSource.from_url(url, loop=self.bot.loop)
        except DownloadError:
            return await ctx.send("Couldn't find any video with that name. Try something else.")
        try:
            ctx.voice_client.play(player, after=lambda e: print('Player error: %s' % e) if e else None)
        except discord.Forbidden:
            return await ctx.send("I don't have permissions to play in this channel.")
        em = discord.Embed(color=discord.Color(value=0x00ff00), title=f"Playing")
        em.description = player.title
        em.set_author(name=ctx.author.name, icon_url=ctx.author.avatar_url)
        em.add_field(name='Volume', value=player.volume)
        msg = await ctx.send(embed=em)
        try:
            await msg.add_reaction("\U000023f8") # Pause
            await msg.add_reaction("\U000025b6") # Play
            await msg.add_reaction("\U000023f9") # Stop
            await msg.add_reaction("\U0001f501") # Repeat
            await msg.add_reaction("\U00002753") # Help
        except discord.Forbidden:
            return await ctx.send("I don't have Add Reaction permissions, so I can't show my awesome playing panel!")
        try:    
            while True:
                reaction, user = await self.bot.wait_for('reaction_add', check=lambda reaction, user: user == ctx.author)
                if reaction.emoji == ":stop_button:":
                    await msg.delete()
                    break
                elif reaction.emoji == "⏸":
                    ctx.voice_client.pause()
                    await msg.remove_reaction("\U000023f8", ctx.author)
                elif reaction.emoji == "▶":
                    ctx.voice_client.resume()
                    await msg.remove_reaction("\U000025b6", ctx.author)
                elif reaction.emoji == "🔁":
                    ctx.voice_client.play(player, after=lambda e: print('Player error: %s' % e) if e else None)
                    await msg.remove_reaction("\U0001f501", ctx.author)
                elif reaction.emoji == "❓":
                    embed = discord.Embed(color=discord.Color(value=0x00ff00), title='Music Player Help')
                    embed.description = "**What do these magical buttons do?** \n\n:pause_button: Pauses the current song.\n:arrow_forward: Resumes any currently paused song.\n:stop_button: Stops the playing song and deletes this message.\n:repeat: Starts the current song from the beginning.\n:question: Shows this message."
                    embed.set_footer(text='This will revert back in 15 seconds.')
                    await msg.edit(embed=embed)
                    await asyncio.sleep(15)
                    await msg.edit(embed=em)    
        except discord.Forbidden:
            return await ctx.send("I can't remove your reactions! Ouch.")
        except Exception as e:
            return await ctx.send(f"An unknown error occured. Details: \n\n```{e}```")


    @commands.command()
    async def pause(self, ctx):
        """Pauses whatever is playing."""
        if ctx.voice_client is None:
            return await ctx.send("How do I pause without me connected to a voice channel?")
        ctx.voice_client.pause()
        await ctx.send("**I am now paused.** :pause_button: ")


    @commands.command()
    async def resume(self, ctx):
        """Resumes whatever isn't playing."""
        if ctx.voice_client is None:
            return await ctx.send("How do I pause without me connected to a voice channel?")
        ctx.voice_client.resume()
        await ctx.send("**Carrying on!** :pause_button: ")


def setup(bot):
    bot.add_cog(Music(bot))

