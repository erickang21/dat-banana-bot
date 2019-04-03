#Code written by Pixel so he doesn't gag anymore
import discord
import lavalink
import logging
import re
from discord.ext import commands
time_rx = re.compile('[0-9]+')
url_rx = re.compile('https?:\/\/(?:www\.)?.+')

class Music(commands.Cog): #Line 6-36 copied from Lavalink.py/music-v2.py since I cba to write it myself (Line 31 modified)
    def __init__(self, bot):
        self.bot = bot

        if not hasattr(bot, 'lavalink'):
            lavalink.Client(bot=bot, password=bot.config.ll_password, loop=bot.loop, log_level=logging.DEBUG,ws_port=bot.config.ll_port,rest_port=bot.config.ll_port)
            self.bot.lavalink.register_hook(self._track_hook)

    def cog_unload(self):
        for guild_id, player in self.bot.lavalink.players:
            self.bot.loop.create_task(player.disconnect())
            player.cleanup()

        # Clears the players from Lavalink's internal cache
        self.bot.lavalink.players.clear()
        self.bot.lavalink.unregister_hook(self._track_hook)

    async def _track_hook(self, event):
        if isinstance(event, lavalink.Events.StatsUpdateEvent):
            return
        channel = self.bot.get_channel(event.player.fetch('channel'))
        if not channel:
            return

        if isinstance(event, lavalink.Events.TrackStartEvent):
            return

        elif isinstance(event, lavalink.Events.QueueEndEvent):
            return
        
       

    @commands.command(brief="Make me play your gucci music")
    @commands.guild_only()
    async def play(self, ctx, *, query: str):
        player = self.bot.lavalink.players.get(ctx.guild.id)
     
        query = query.strip('<>')
     
        if not url_rx.match(query):
            query = f"ytsearch:{query}"
        query = await self.bot.utils.clean_text(ctx, query)
        msg = await ctx.send(f"I'm on it! Searching for **{query}** {discord.utils.get(self.bot.emojis,id=453323479555506188)}") #how to avoid everyone exploits
        tracks = await self.bot.lavalink.get_tracks(query)
        if not tracks:
            return msg.edit(content=f"Uh-oh! It looks like nothing was found. Maybe your query was a bit *too creative...*")

        if 'list' in query and 'ytsearch:' not in query:
            return msg.edit(content=f"Dang. I don't support playlists yet.")

        player.add(requester=ctx.author.id, track=tracks["tracks"][0])

        if not player.is_playing:
            await player.play()
            track_name = await self.bot.utils.clean_text(ctx, tracks['tracks'][0]['info']['title'])
            await ctx.send(f"Gottem! I'm now playing **{track_name}**. {discord.utils.get(self.bot.emojis,id=559923444234584064)}")
        else:
            await ctx.send(f"Gottem! But something is playing already. I've added **{track_name}** to the queue! {self.bot.get_emoji(522530578860605442)}")



    @commands.command()
    @commands.guild_only()
    async def queue(self, ctx):
        player = self.bot.lavalink.players.get(ctx.guild.id)

        if not player.queue:
            return await ctx.send(f"I don't have anything queued up.")

        queue_list = ""
        ind = 0
        for track in player.queue:
            ind = ind + 1
            queue_list += f"{ind}) **{track.title}**"
        em = discord.Embed(color=ctx.author.color, title="Music Queue")
        em.set_author(name=ctx.guild.name, icon_url=ctx.guild.icon_url)
        em.description = queue_list
        await ctx.send(embed=em)


    @commands.command()
    @commands.guild_only()
    async def pause(self, ctx):
        player = self.bot.lavalink.players.get(ctx.guild.id)

        if not player.is_playing:
            return await ctx.send(f"I'm not playing anything! {self.bot.get_emoji(538496161322106920)}")

        if not player.paused:
            await player.set_pause(True)
            await ctx.send(f"Paused. :pause_button:")


    @commands.command()
    @commands.guild_only()
    async def resume(self, ctx):
        player = self.bot.lavalink.players.get(ctx.guild.id)

        if not player.is_playing:
            return await ctx.send(f"I'm not playing anything! {self.bot.get_emoji(538496161322106920)}")

        if player.paused:
            await player.set_pause(False)
            await ctx.send(f"Resumed. :arrow_forward:")


    @commands.command()
    @commands.guild_only()
    async def disconnect(self, ctx):
        player = self.bot.lavalink.players.get(ctx.guild.id)

        if not player.is_connected:
            return await ctx.send("I am not connected to a VC")

        if not ctx.author.voice or (player.is_connected and ctx.author.voice.channel.id != int(player.channel_id)):
            return await ctx.send(f"You're not in my VC. Or my league. {self.bot.get_emoji(453320099999252493)}")

        player.queue.clear()
        await player.disconnect()
        await ctx.send(f"Alright, I'm out of here. The queue has been cleared too. {self.bot.get_emoji(481184449883537418)}")


    @play.before_invoke
    async def ensure_voice(self, ctx): #Below is copied because I literally could not be assed
        """ A few checks to make sure the bot can join a voice channel. """
        player = self.bot.lavalink.players.get(ctx.guild.id)

        if not player.is_connected:
            if not ctx.author.voice or not ctx.author.voice.channel:
                return await ctx.send("You are not in a voice channel, so no")
                

            permissions = ctx.author.voice.channel.permissions_for(ctx.me)

            if not permissions.connect or not permissions.speak:
                return await ctx.send("I am missing permissions to connect/speak in that Voice Channel")
                

            player.store('channel', ctx.channel.id)
            await player.connect(ctx.author.voice.channel.id)
        else:
            if player.connected_channel.id != ctx.author.voice.channel.id:
                return await ctx.send("You are not in my voice channel, so no")


def setup(bot):
    bot.add_cog(Music(bot))
