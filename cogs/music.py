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
    async def from_url(cls, url, *, loop=None):
        loop = loop or asyncio.get_event_loop()
        data = await loop.run_in_executor(None, lambda: ytdl.extract_info(url, download=False))

        if 'entries' in data:
            data = data['entries'][0]
   
        return cls(discord.FFmpegPCMAudio(data['url'], **ffmpeg_options), data=data)




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
        duration = player.get_duration()
        em.set_author(name=ctx.author.name, icon_url=ctx.author.avatar_url)
        minutes, seconds = divmod(duration, 60)
        em.add_field(name='Length', value=f"{str(minutes)}:{str(seconds).replace('0', '00').replace('1', '01').replace('2', '02').replace('3', '03').replace('4', '04').replace('5', '05').replace('6', '06').replace('7', '07').replace('8', '08').replace('9', '09')}")
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
        # except Exception as e:
        #     return await ctx.send(f"An unknown error occured. Details: \n\n```{e}```")

        # This made shit way too spammy, can't think of a good way to avoid it, rather just remove it.

    def get_lines(self, number):
        number = int(number)
        if number >= 0 and number <= 10:
            return "||||||||||"
        elif number >= 10 and number <= 20:
            return "**|**||||||||"
        elif number >= 20 and number <= 30:
            return "**||**||||||||"
        elif number >= 30 and number <= 40:
            return "**|||**|||||||"
        elif number >= 40 and number <= 50:
            return "**||||**||||||"
        elif number >= 50 and number <= 60:
            return "**|||||**|||||"
        elif number >= 60 and number <= 70:
            return "**||||||**||||"
        elif number >= 70 and number <= 80:
            return "**|||||||**|||"
        elif number >= 80 and number <= 90:
            return "**||||||||**||"
        elif number >= 90 and number <= 99:
            return "**|||||||||**|"
        elif number == 100:
            return "**||||||||||**"


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
            duration = player.get_duration()
            minutes, seconds = divmod(duration, 60)
            em.add_field(name='Length', value=f"{str(minutes)}:{str(seconds).replace('0', '00').replace('1', '01').replace('2', '02').replace('3', '03').replace('4', '04').replace('5', '05').replace('6', '06').replace('7', '07').replace('8', '08').replace('9', '09')}")
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
                await ctx.send("I can't remove your reactions! Ouch.")
            # except Exception as e:
            #     return await ctx.send(f"An unknown error occured. Details: \n\n```{e}```")

            # This made shit way too spammy, can't think of a good way to avoid it, rather just remove it.
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
            duration = to_play.get_duration()
            minutes, seconds = divmod(duration, 60)
            em.add_field(name='Length', value=f"{str(minutes)}:{str(seconds).replace('0', '00').replace('1', '01').replace('2', '02').replace('3', '03').replace('4', '04').replace('5', '05').replace('6', '06').replace('7', '07').replace('8', '08').replace('9', '09')}")
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
        try:
            song_list = self.queue[str(ctx.guild.id)]
        except KeyError:
            em.description = "No songs are currently in the queue! Just queue the :banana: song, kthx."
            return await ctx.send(embed=em)
        songs = ""
        count = 0
        for x in song_list:
            count += 1
            songs += f"{str(count)}: **{x.title}**\n"
        em.description = songs if song_list != [] else "No songs are currently in the queue! Just queue the :banana: song, kthx."
        await ctx.send(embed=em)


    @commands.command()
    async def volume(self, ctx):
        """Change or view the current volume for playing."""
        if not ctx.voice_client:
            return await ctx.send("Nothing is playing! Cannot detect volume or change it.")
        vol = ctx.voice_client.source.volume * 100
        msg = await ctx.send(f":loud_sound: Volume for **{ctx.voice_client.channel.name}**:\n{self.get_lines(vol)} {vol}\n\n**How to use:**\n:heavy_plus_sign:: Increases the volume by 5.\n:heavy_minus_sign:: Decrease the volume by 5.")
        await msg.add_reaction("\U00002795")
        await msg.add_reaction("\U00002796")
        while ctx.voice_client.is_playing():
            reaction, user = await self.bot.wait_for('reaction_add', check=lambda reaction, user: user == ctx.author)
            if reaction.emoji == '➕':
                vol = vol + 5
                ctx.voice_client.source.volume = vol / 100
                try:
                    await msg.remove_reaction("\U00002795", ctx.author)
                except discord.Forbidden:
                    await ctx.send("I can't remove your reactions! Ouch.")
                await msg.edit(content=f":loud_sound: Volume for **{ctx.voice_client.channel.name}**:\n{self.get_lines(vol)} {vol}\n\n**How to use:**\n:heavy_plus_sign:: Increases the volume by 5.\n:heavy_minus_sign:: Decrease the volume by 5.")
            elif reaction.emoji == '➖':
                vol = vol - 5
                ctx.voice_client.source.volume = vol / 100
                try:
                    await msg.remove_reaction("\U00002796", ctx.author)
                except discord.Forbidden:
                    await ctx.send("I can't remove your reactions! Ouch.")
                await msg.edit(content=f":loud_sound: Volume for **{ctx.voice_client.channel.name}**:\n{self.get_lines(vol)} {vol}\n\n**How to use:**\n:heavy_plus_sign:: Increases the volume by 5.\n:heavy_minus_sign:: Decrease the volume by 5.")
        

def setup(bot):
    bot.add_cog(Music(bot))

