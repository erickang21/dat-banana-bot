import discord
from discord.ext import commands
import datetime
import sys
import textwrap
import asyncio
import os
import json
import lavalink
import logging
from discord.ext.commands.cooldowns import BucketType  
from bs4 import BeautifulSoup
from .utils.utils import Utils

class Music:
    def __init__(self, bot):
        self.bot = bot
        self.utils = Utils(bot)
        if not hasattr(bot, 'lavalink'):
            with open("data/apikeys.json") as file:
                apikeys = json.load(file)
                lavalink.Client(bot, loop=self.bot.loop, host=apikeys["ll_host"], password=apikeys["ll_password"], ws_port=apikeys["ll_port"])
                self.bot.lavalink.register_hook(self.track_hook)
        self.skip_count = {}

    async def track_hook(self, e):
        if isinstance(e, lavalink.Events.QueueEndEvent):
            await e.player.disconnect()
        if isinstance(e, lavalink.Events.TrackEndEvent):
            await e.player.play()
        if isinstance(e, lavalink.Events.TrackStartEvent):
            ctx = e.player.fetch("ctx")
            em = discord.Embed(color=0x00ff00, title=f"Playing")
            #em.description = f"**{e.track.title}**"
            em.set_author(name=e.track.requester.name, icon_url=e.track.requester.avatar_url)
            second = e.track.duration / 1000
            minute, second = divmod(second, 60)
            hour, minute = divmod(minute, 60)
            #minutes, seconds = divmod(e.track.duration, 60)
            #em.add_field(name='Length', value=f"{str(minutes)}:{str(seconds).replace('0', '00').replace('1', '01').replace('2', '02').replace('3', '03').replace('4', '04').replace('5', '05').replace('6', '06').replace('7', '07').replace('8', '08').replace('9', '09')}")
            if hour:
                length = f"{int(hour)}:{self.utils.format_time(minute)}:{self.utils.format_time(second)}"
            else:
                length = f"{self.utils.format_time(minute)}:{self.utils.format_time(second)}"
            playing_panel = textwrap.dedent(f"""
            :musical_note: **Song**
            {e.track.title}

            {self.bot.get_emoji(430340802879946773)} **Requested By**
            {str(ctx.author)}

            :timer: **Length**
            {length}

            :loud_sound: **Volume**
            {self.utils.get_lines(e.player.volume)} {e.player.volume}%

            :1234: **Queue Position**
            {len(e.player.queue)}
            """)
            #em.add_field(name='Length', value=length)
            #em.add_field(name='Volume', value=f"{self.utils.get_lines(e.player.volume)} {e.player.volume}%")
            em.description = playing_panel
            #em.add_field(name='Position in Queue', value=len(e.player.queue))
            msg = await ctx.send(embed=em, edit=False)
            try:
                await msg.add_reaction("\U000023f8") # Pause
                await msg.add_reaction("\U000025b6") # Play
                await msg.add_reaction("\U000023f9") # Stop
                await msg.add_reaction("\U0001f501") # Repeat
                await msg.add_reaction("\U00002753") # Help
            except discord.Forbidden:
                return await ctx.send("I don't have Add Reaction permissions, so I can't show my awesome playing panel!")
            try:    
                while e.player.is_playing:
                    reaction, user = await self.bot.wait_for('reaction_add', check=lambda reaction, user: user == ctx.author)
                    if reaction.emoji == "⏸":
                        await e.player.set_pause(True)
                        await msg.remove_reaction("\U000023f8", ctx.author)
                    elif reaction.emoji == "▶":
                        await e.player.set_pause(False)
                        await msg.remove_reaction("\U000025b6", ctx.author)
                    elif reaction.emoji == "⏹":
                        await e.player.stop()
                        await msg.delete()
                    elif reaction.emoji == "🔁":
                        e.player.repeat = not e.player.repeat
                        await msg.remove_reaction("\U0001f501", ctx.author)
                    elif reaction.emoji == "❓":
                        await msg.remove_reaction("\U00002753", ctx.author)
                        embed = discord.Embed(color=0x00ff00, title='Music Player Help')
                        embed.description = "**What do these magical buttons do?** \n\n:pause_button: Pauses the current song.\n:arrow_forward: Resumes any currently paused song.\n:stop_button: Stops the playing song and deletes this message.\n:repeat: Starts the current song from the beginning.\n:question: Shows this message."
                        embed.set_footer(text='This will revert back in 15 seconds.')
                        await msg.edit(embed=embed)
                        await asyncio.sleep(15)
                        await msg.edit(embed=em)    
            except discord.Forbidden:
                pass # No need to send 
            # except Exception as e:
            #     return await ctx.send(f"An unknown error occured. Details: \n\n```{e}```")

            # This made shit way too spammy, can't think of a good way to avoid it, rather just remove it.




    @commands.command()
    @commands.guild_only()
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
    @commands.guild_only()
    async def disconnect(self, ctx):
        '''Disconnects the bot to your current voice channel. Cya!'''
        if ctx.voice_client is None:
            await ctx.send("Looks like I'm not connected to a voice channel yet! Can't disconnect...:thinking:")
        else:
            await ctx.voice_client.disconnect()
            await ctx.send(f"Successfully disconnected from the voice channel. :white_check_mark:")

    @commands.command()
    @commands.guild_only()
    #@commands.cooldown(2, 15.0, BucketType.user)
    async def play(self, ctx, *, search=None):
        player = self.bot.lavalink.players.get(ctx.guild.id)
        """Search for a YouTube video to play, by name."""
        if search is None:
            return await ctx.send("ACK! Provide a search please")
        if not player.is_connected:
            if ctx.author.voice is None:
                return await ctx.send("Looks like you aren't connected to a voice channel yet! Where do I join?")
            player.store("ctx", ctx)
            await player.connect(ctx.author.voice.channel.id)
        em = discord.Embed(color=0x00ff00, title="Searching...", description=f"{self.bot.get_emoji(471279983197814806)} Searching `{search}`...")
        m = await ctx.send(embed=em, edit=False)

        search = search.strip("<>")
        if not search.startswith("http"):
            search = f"ytsearch:{search}"

        tracks = await self.bot.lavalink.get_tracks(search)

        if not tracks:
            await ctx.send("OOF, No results found. Looks like that search returned zero results! Right?")

        await m.delete()
        player.add(requester=ctx.author, track=tracks['tracks'][0])

        if not player.is_playing:
            await player.play()
            em = discord.Embed(color=0x00ff00, title=f"Playing")
            #em.description = f"**{e.track.title}**"
            em.set_author(name=player.current.requester.name, icon_url=player.current.requester.avatar_url)
            second = player.current.duration / 1000
            minute, second = divmod(second, 60)
            hour, minute = divmod(minute, 60)
            #minutes, seconds = divmod(player.track.duration, 60)
            #em.add_field(name='Length', value=f"{str(minutes)}:{str(seconds).replace('0', '00').replace('1', '01').replace('2', '02').replace('3', '03').replace('4', '04').replace('5', '05').replace('6', '06').replace('7', '07').replace('8', '08').replace('9', '09')}")
            if hour:
                length = f"{int(hour)}:{self.utils.format_time(minute)}:{self.utils.format_time(second)}"
            else:
                length = f"{self.utils.format_time(minute)}:{self.utils.format_time(second)}"
            playing_panel = textwrap.dedent(f"""
            :musical_note: **Song**
            {player.current.title}

            {self.bot.get_emoji(430340802879946773)} **Requested By**
            {str(ctx.author)}

            :timer: **Length**
            {length}

            :loud_sound: **Volume**
            {self.utils.get_lines(player.volume)} {player.volume}%

            :1234: **Queue Position**
            {len(player.queue)}
            """)
            #em.add_field(name='Length', value=length)
            #em.add_field(name='Volume', value=f"{self.utils.get_lines(player.player.volume)} {player.player.volume}%")
            em.description = playing_panel
            #em.add_field(name='Position in Queue', value=len(player.player.queue))
            msg = await ctx.send(embed=em, edit=False)
            try:
                await msg.add_reaction("\U000023f8") # Pause
                await msg.add_reaction("\U000025b6") # Play
                await msg.add_reaction("\U000023f9") # Stop
                await msg.add_reaction("\U0001f501") # Repeat
                await msg.add_reaction("\U00002753") # Help
            except discord.Forbidden:
                return await ctx.send("I don't have Add Reaction permissions, so I can't show my awesome playing panel!")
            try:    
                while player.player.is_playing:
                    reaction, user = await self.bot.wait_for('reaction_add', check=lambda reaction, user: user == ctx.author)
                    if reaction.emoji == "⏸":
                        await player.set_pause(True)
                        await msg.remove_reaction("\U000023f8", ctx.author)
                    elif reaction.emoji == "▶":
                        await player.set_pause(False)
                        await msg.remove_reaction("\U000025b6", ctx.author)
                    elif reaction.emoji == "⏹":
                        await player.stop()
                        await msg.delete()
                    elif reaction.emoji == "🔁":
                        player.repeat = not player.player.repeat
                        await msg.remove_reaction("\U0001f501", ctx.author)
                    elif reaction.emoji == "❓":
                        await msg.remove_reaction("\U00002753", ctx.author)
                        embed = discord.Embed(color=0x00ff00, title='Music Player Help')
                        embed.description = "**What do these magical buttons do?** \n\n:pause_button: Pauses the current song.\n:arrow_forward: Resumes any currently paused song.\n:stop_button: Stops the playing song and deletes this message.\n:repeat: Starts the current song from the beginning.\n:question: Shows this message."
                        embed.set_footer(text='This will revert back in 15 seconds.')
                        await msg.edit(embed=embed)
                        await asyncio.sleep(15)
                        await msg.edit(embed=em)    
            except discord.Forbidden:
                pass
        else:
            await ctx.send(":ok_hand: **{}** was enqueued!".format(await Utils.clean_text(ctx, tracks['tracks'][0]["info"]["title"])))

    @commands.command()
    @commands.guild_only()
    async def pause(self, ctx):
        """Pauses whatever is playing."""
        player = self.bot.lavalink.players.get(ctx.guild.id)
        if not player.is_playing:
            return await ctx.send("How do I pause without me connected playing anything?")
        await player.set_pause(True)
        await ctx.send("**I am now paused.** :pause_button: ")


    @commands.command()
    @commands.guild_only()
    async def resume(self, ctx):
        """Resumes whatever isn't playing."""
        player = self.bot.lavalink.players.get(ctx.guild.id)
        if not player.is_playing:
            return await ctx.send("How do I resume without me connected playing anything?")
 
        await player.set_pause(False)
        await ctx.send("**Carrying on!** :arrow_forward:")
       
    @commands.command()
    @commands.has_permissions(manage_guild=True)
    @commands.guild_only()
    async def stop(self, ctx):
        """Stops the player."""
        player = self.bot.lavalink.players.get(ctx.guild.id)
        if not player.is_playing:
            return await ctx.send("How do I stop the music without me connected playing anything?")

        player.queue.clear()
        await player.stop()
        await ctx.send("**HALT!** Music has been stopped. :stop_button:")

    @commands.command()
    @commands.guild_only()
    async def skip(self, ctx):
        """Skip the currently playing song."""
        if not ctx.author.guild_permissions.manage_guild:
            
            try:
                count = self.skip_count[str(ctx.guild.id)] 
                self.skip_count[str(ctx.guild.id)] += 1
                await ctx.send("**Are we skipping this song?**\n\n(You don't have Manage Server, so I'm waiting for 2 votes to skip this song.\n\n**Votes:** 1/2")
            except KeyError:
                count = self.skip_count[str(ctx.guild.id)] = 1  
                await ctx.send("**Are we skipping this song?**\n\n(You don't have Manage Server, so I'm waiting for 2 votes to skip this song.\n\n**Votes:** 1/2")   
            if count == 2:
                self.skip_count[str(ctx.guild.id)] = 0
                await self.bot.lavalink.players.get(ctx.guild.id).skip()
                await ctx.author.voice.channel.connect()
                return await ctx.send("Alright! We skipped the song. :fast_forward:")
        else:
            await self.bot.lavalink.players.get(ctx.guild.id).skip()
            try:
                await ctx.author.voice.channel.connect()
            except:
                pass
            player = self.bot.lavalink.players.get(ctx.guild.id)
            await player.play()
            return await ctx.send("Alright! We skipped the song. :fast_forward:\n\n(You have Manage Server, so I went full steam ahead.)")

    @commands.command()
    @commands.guild_only()
    async def queue(self, ctx):
        """Gets the queue for the server."""
        player = self.bot.lavalink.players.get(ctx.guild.id)
        if not player.queue:
            return await ctx.send("No songs are currently in the queue! Just queue the :banana: song, kthx.")
        em = discord.Embed(color=0x00ff00, title=f"Music Queue")
        em.set_author(name=ctx.guild.name, icon_url=ctx.guild.icon_url)
        songs = ""
        count = 0
        for x in player.queue:
            count += 1
            songs += f"{str(count)}: **{x.title}**\n"
        em.description = songs
        await ctx.send(embed=em)

    @commands.command()
    async def lyrics(self, ctx, *, song: str = None):
        """Get lyrics for a song or finds lyrics for the current playing song."""
        player = self.bot.lavalink.players.get(ctx.guild.id)
        if player and song == None:
            song = player.queue[0].title

        async with ctx.typing():
            res = await (await self.bot.session.get(f"https://api.genius.com/search?q={song}", headers={"Authorization": f"Bearer {self.bot.config.geniusapi}"})).json()

        if not res["response"]["hits"]:
            return await ctx.send("No lyrics found. Try looking for something different!")
        
        res1 = await (await self.bot.session.get(res["response"]["hits"][0]["result"]["url"])).text()
        scraped = BeautifulSoup(res1, "lxml")

        if not scraped.find_all("p"):
            return await ctx.send("No lyrics found. Try looking for something different!")

        description = scraped.find_all("p")[0].text
        if len(description) > 2045:
            description = f"{description[:2045]}..."
        
        embed = discord.Embed(title=res["response"]["hits"][0]["result"]["full_title"], color=0xFF00FF)
        embed.description = description
        embed.set_footer(text="Powered by: https://genius.com", icon_url=ctx.author.avatar_url)
        embed.set_thumbnail(url=res["response"]["hits"][0]["result"]["header_image_thumbnail_url"])
        await ctx.send(embed=embed)

    @commands.command()
    @commands.guild_only()
    async def volume(self, ctx):
        """Change or view the current volume for playing."""
        player = self.bot.lavalink.players.get(ctx.guild.id)
        if not player.is_playing:
            return await ctx.send("Nothing is playing! Cannot detect volume or change it.")
        msg = await ctx.send(f":loud_sound: Volume for **{ctx.guild.name}**:\n{self.utils.get_lines(player.volume)} {player.volume}\n\n**How to use:**\n:heavy_plus_sign:: Increases the volume by 5.\n:heavy_minus_sign:: Decrease the volume by 5.")
        await msg.add_reaction("\U00002795")
        await msg.add_reaction("\U00002796")
        while player.is_playing:
            reaction, user = await self.bot.wait_for('reaction_add', check=lambda reaction, user: user == ctx.author)
            if reaction.emoji == '➕':
                if player.volume > 100:
                    break # Ignore volumes that are greater than 100
                await player.set_volume(player.volume + 5)
                try:
                    await msg.remove_reaction("\U00002795", ctx.author)
                except discord.Forbidden:
                    await ctx.send("I can't remove your reactions! Ouch.")
                await msg.edit(content=f":loud_sound: Volume for **{ctx.guild.name}**:\n{self.utils.get_lines(player.volume)} {player.volume}\n\n**How to use:**\n:heavy_plus_sign:: Increases the volume by 5.\n:heavy_minus_sign:: Decrease the volume by 5.")
            elif reaction.emoji == '➖':
                await player.set_volume(player.volume - 5)
                try:
                    await msg.remove_reaction("\U00002796", ctx.author)
                except discord.Forbidden:
                    await ctx.send("I can't remove your reactions! Ouch.")
                await msg.edit(content=f":loud_sound: Volume for **{ctx.guild.name}**:\n{self.utils.get_lines(player.volume)} {player.volume}\n\n**How to use:**\n:heavy_plus_sign:: Increases the volume by 5.\n:heavy_minus_sign:: Decrease the volume by 5.")





def setup(bot):
    bot.add_cog(Music(bot))
