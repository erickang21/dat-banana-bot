import discord
from discord.ext import commands
import datetime
import sys
import textwrap
import asyncio
import os
import json
import logging
from discord.ext.commands.cooldowns import BucketType
from bs4 import BeautifulSoup

class Music:
    def __init__(self, bot):
        self.bot = bot
        self.utils = self.bot.utils
        self.skip_count = {}

    @commands.command()
    @commands.guild_only()
    async def connect(self, ctx):
        '''Connects the bot to your current voice channel.'''
        if ctx.author.voice is None:
            return await ctx.send("Looks like you aren't connected to a voice channel yet! Where do I join?")
        if ctx.voice_client is None:
            await self.bot.audio_manager.get_player(ctx)
            await ctx.send(f"Successfully connected to Voice Channel **{ctx.author.voice.channel.name}**. :white_check_mark:")
        else:
            await self.bot.audio_manager.get_player(ctx)
            await ctx.send(f"Successfully connected to Voice Channel: **{ctx.author.voice.channel.name}**. :white_check_mark:")


    @commands.command()
    @commands.guild_only()
    async def disconnect(self, ctx):
        '''Disconnects the bot to your current voice channel. Cya!'''
        if ctx.voice_client is None:
            await ctx.send("Looks like I'm not connected to a voice channel yet! Can't disconnect...:thinking:")
        else:
            await self.bot.audio_manager.leave(ctx)
            await ctx.send(f"Successfully disconnected from the voice channel. :white_check_mark:")

    @commands.command()
    @commands.guild_only()
    #@commands.cooldown(2, 15.0, BucketType.user)
    async def play(self, ctx, *, search=None):
        player = self.bot.audio_manager.get_player(ctx)
        """Search for a YouTube video to play, by name."""
        if search is None:
            return await ctx.send("ACK! Provide a search please")
        if not player.is_connected:
            if ctx.author.voice is None:
                return await ctx.send("Looks like you aren't connected to a voice channel yet! Where do I join?")
            await self.bot.audio_manager.connect(ctx)
        em = discord.Embed(color=0x00ff00, title="Searching...", description=f"{self.bot.get_emoji(471279983197814806)} Searching `{search}`...")
        m = await ctx.send(embed=em, edit=False)

        search = search.strip("<>")
        if not search.startswith("http"):
            search = f"ytsearch:{search}"

        tracks = await self.bot.audio_manager.get_tracks(player, search)

        if not tracks:
            await ctx.send("OOF, No results found. Looks like that search returned zero results!")

        await m.delete()
        player.add(requester=ctx.author, track=tracks['tracks'][0])

        if not player.playing:
            await player.play()
        else:
            await ctx.send(":ok_hand: **{}** was enqueued!".format(await self.utils.clean_text(ctx, tracks['tracks'][0]["info"]["title"])))

    @commands.command()
    @commands.guild_only()
    async def pause(self, ctx):
        """Pauses whatever is playing."""
        player = self.bot.audio_manager.get_player(ctx)
        if not player.is_playing:
            return await ctx.send("How do I pause without me connected playing anything?")
        await player.set_paused(True)
        await ctx.send("**I am now paused.** :pause_button: ")


    @commands.command()
    @commands.guild_only()
    async def resume(self, ctx):
        """Resumes whatever isn't playing."""
        player = self.bot.audio_manager.get_player(ctx)
        if not player.is_playing:
            return await ctx.send("How do I resume without me connected playing anything?")
 
        await player.set_paused(False)
        await ctx.send("**Carrying on!** :arrow_forward:")
       
    @commands.command()
    @commands.has_permissions(manage_guild=True)
    @commands.guild_only()
    async def stop(self, ctx):
        """Stops the player."""
        player = self.bot.audio_manager.get_player(ctx)
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
                await self.bot.audio_manager.get_player(ctx).play()
                await self.bot.audio_manager.get_player(ctx)
                return await ctx.send("Alright! We skipped the song. :fast_forward:")
        else:
            player = self.bot.audio_manager.get_player(ctx)
            await player.play()
            return await ctx.send("Alright! We skipped the song. :fast_forward:\n\n(You have Manage Server, so I went full steam ahead.)")

    @commands.command()
    @commands.guild_only()
    async def queue(self, ctx):
        """Gets the queue for the server."""
        player = self.bot.audio_manager.get_player(ctx)
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
        player = self.bot.audio_manager.get_player(ctx)
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
        player = self.bot.audio_manager.get_player(ctx)
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
