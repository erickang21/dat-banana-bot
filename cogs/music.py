#Code written by Pixel so he doesn't gag anymore
import discord
import lavalink
from discord.ext import commands
time_rx = re.compile('[0-9]+')
url_rx = re.compile('https?:\/\/(?:www\.)?.+')

class Music(commands.Cog): #Line 6-36 copied from Lavalink.py/music-v2.py since I cba to write it myself (Line 31 modified)
    def __init__(self, bot):
        self.bot = bot

        if not hasattr(bot, 'lavalink'):
            lavalink.Client(bot=bot, password='youshallnotpass', loop=bot.loop, log_level=logging.DEBUG)
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
        
       

@commands.command
@commands.guild_only()
async def play(self,ctx,*,query : str):
    player = self.bot.lavalink.players.get(ctx.guild.id)
    
    query = query.strip('<>')
    
    if not url_rx.match(query):
        query = f"ytsearch:{query}"
       
    msg = await ctx.send(f"Okay! Now searching for ``{query}`` {discord.utils.get(self.bot.emojis,id=453323479555506188)}") #how to avoid everyone exploits
    
    if not tracks:
        return msg.edit(f"Nothing was found ``{query}``. Please check that you didnt spell anything wrong")
    
    if 'list' in query and 'ytsearch:' not in query:
        return msg.edit(f"Oops! I don't support playlists yet")
    
    player.add(requester=ctx.author.id, track=tracks[0])
    
    if not player.is_playing():
        await player.play()
        await ctx.send(f"Got it! Now playing the gucci music known as ``{tracks[0]['info']['title']}`` {discord.utils.get(self.bot.emojis,id=559923444234584064)}")
