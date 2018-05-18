import discord
from discord.ext import commands
import datetime
import sys
import asyncio
import os
import aiohttp
import json
import youtube_dl
from discord.ext.commands.cooldowns import BucketType


YOUTUBE_DL_OPTIONS = {
    'format': 'bestaudio/best',
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

    def get_duration(self):
        return self.data.get('duration')

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
       self.queue = {}

    async def next_song(self, ctx, loop):
        if len(self.queue[str(ctx.guild.id)]) is 0:
            await ctx.voice_client.disconnect()
            await ctx.send("No songs are left in the queue... Just queue the 🍌 song.")
        #player = await YTDLSource.from_url(self.queue[str(ctx.guild.id)][0], loop=loop)
        player = self.queue[str(ctx.guild.id)][0]
        ctx.voice_client.play(player, after=lambda e: asyncio.run_coroutine_threadsafe(self.next_song(ctx, loop), loop=self.bot.loop).result())
        self.queue[str(ctx.guild.id)].remove(self.queue[str(ctx.guild.id)][0])
        em = discord.Embed(color=discord.Color(value=0x00ff00), title=f"Playing")
        em.description = player.title
        em.set_author(name=ctx.author.name, icon_url=ctx.author.avatar_url)
        em.add_field(name='Length', value=f"{int(int(player.get_duration())/60)}:{int(player.get_duration()) - int(int(player.get_duration())/60)*60}")
        em.add_field(name='Volume', value=player.volume)
        em.add_field(name='Position in Queue', value=len(self.queue[str(ctx.guild.id)]))
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
            while ctx.voice_client.is_playing():
                reaction, user = await self.bot.wait_for('reaction_add', check=lambda reaction, user: user == ctx.author)
                if reaction.emoji == "⏸":
                    ctx.voice_client.pause()
                    await msg.remove_reaction("\U000023f8", ctx.author)
                elif reaction.emoji == "▶":
                    ctx.voice_client.resume()
                    await msg.remove_reaction("\U000025b6", ctx.author)
                elif reaction.emoji == "⏹":
                    ctx.voice_client.stop()
                    await msg.delete()
                elif reaction.emoji == "🔁":
                    ctx.voice_client.stop()
                    ctx.voice_client.play(next, after=lambda e: print('Player error: %s' % e) if e else None)
                    await msg.remove_reaction("\U0001f501", ctx.author)
                elif reaction.emoji == "❓":
                    await msg.remove_reaction("\U00002753", ctx.author)
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
    #@commands.cooldown(2, 15.0, BucketType.user)
    async def play(self, ctx, *, url):
        """Search for a YouTube video to play, by name."""
        if ctx.author.voice is None:
            return await ctx.send("Looks like you aren't connected to a voice channel yet! Where do I join?")
        if ctx.voice_client is None:
            await ctx.author.voice.channel.connect()
        em = discord.Embed(color=discord.Color(value=0x00ff00), title="Searching...", description=f"{self.bot.get_emoji(441385713091477504)} Searching `{url}`...")
        m = await ctx.send(embed=em)
        if not ctx.voice_client.is_playing():
            try:            
                player = await YTDLSource.from_url(url, loop=self.bot.loop)
            except youtube_dl.DownloadError:
                return await ctx.send("Couldn't find any video with that name. Try something else.")        
            try:
                ctx.voice_client.play(player, after=lambda e: asyncio.run_coroutine_threadsafe(self.next_song(ctx, self.bot.loop), loop=self.bot.loop).result())
            except discord.Forbidden:
                return await ctx.send("I don't have permissions to play in this channel.")
            await m.delete()
            em = discord.Embed(color=discord.Color(value=0x00ff00), title=f"Playing")
            em.description = f"**{player.title}**"
            em.set_author(name=ctx.author.name, icon_url=ctx.author.avatar_url)
            em.add_field(name='Length', value=f"{int(int(player.get_duration())/60)}:{int(player.get_duration()) - int(int(player.get_duration())/60)*60}")
            em.add_field(name='Volume', value=player.volume)
            em.add_field(name='Position in Queue', value='0')
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
                while ctx.voice_client.is_playing():
                    reaction, user = await self.bot.wait_for('reaction_add', check=lambda reaction, user: user == ctx.author)
                    if reaction.emoji == "⏸":
                        ctx.voice_client.pause()
                        await msg.remove_reaction("\U000023f8", ctx.author)
                    elif reaction.emoji == "▶":
                        ctx.voice_client.resume()
                        await msg.remove_reaction("\U000025b6", ctx.author)
                    elif reaction.emoji == "⏹":
                        ctx.voice_client.stop()
                        await msg.delete()
                    elif reaction.emoji == "🔁":
                        ctx.voice_client.stop()
                        ctx.voice_client.play(player, after=lambda e: print('Player error: %s' % e) if e else None)
                        await msg.remove_reaction("\U0001f501", ctx.author)
                    elif reaction.emoji == "❓":
                        await msg.remove_reaction("\U00002753", ctx.author)
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
        else:
            try:
                to_play = await YTDLSource.from_url(url, loop=self.bot.loop)
            except youtube_dl.DownloadError:
                return await ctx.send("Couldn't find any video with that name. Try something else.")
            try:
                self.queue[str(ctx.guild.id)].append(to_play)
            except KeyError:
                self.queue[str(ctx.guild.id)] = [to_play]
            em = discord.Embed(color=discord.Color(value=0x00ff00), title='Added to queue!')
            em.description = f"**{to_play.title}**"
            em.add_field(name='Position in Queue', value=len(
                self.queue[str(ctx.guild.id)]))
            dur = int(to_play.get_duration())
            em.add_field(name='Length', value=f"{int(dur/60)}:{str(int(dur) - int(dur)/60*60).replace('0', '00').replace('1', '01').replace('2', '02').replace('3', '03').replace('4', '04').replace('5', '05').replace('6', '06').replace('7', '07').replace('8', '08').replace('9', '09')}")
            em.set_author(name=f"Played by: {ctx.author.name}", icon_url=ctx.author.avatar_url)
            await ctx.send(embed=em)

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
            return await ctx.send("How do I resume without me connected to a voice channel?")
        ctx.voice_client.resume()
        await ctx.send("**Carrying on!** :arrow_forward:")

    @commands.command()
    async def stop(self, ctx):
        """Stops the current song."""
        if ctx.voice_client is None:
            return await ctx.send("How do I resume without me connected to a voice channel?")
        ctx.voice_client.stop()
        await ctx.send("**HALT!** Music has been stopped. :stop_button:")


    @commands.command(name="queue")
    async def _queue(self, ctx):
        """Gets the queue for the server."""
        em = discord.Embed(color=discord.Color(value=0x00ff00), title=f"Music Queue")
        em.set_author(name=ctx.guild.name, icon_url=ctx.guild.icon_url)
        songs = ""
        count = 0
        for x in self.queue[str(ctx.guild.id)]:
            count += 1
            songs += f"{str(count)}: **{x.title}**\n"
        em.description = songs if self.queue[str(ctx.guild.id)] != [] else "No songs are currently in the queue! Just queue the :banana: song, kthx."
        await ctx.send(embed=em)

def setup(bot):
    bot.add_cog(Music(bot))

