import json
import discord
import textwrap
import asyncio
#from .cogs.utils.utils import Utils
from .AudioNode import AudioNode
from .AudioPlayer import AudioPlayer
from .Events import TrackStart

class AudioManager:
    """
    Class of the AudioManager section.
    This is main class and controls all stuff like joining channels, leaving channels, and launching nodes.
    """
    def __init__(self, bot, nodes, shards=1):
        self.bot = bot
        bot.add_listener(self.on_socket_response)
        self.nodes = {}
        self.players = {}
        self._nodes = nodes
        self.shards = shards
        self.session = self.bot.session
        self.utils = self.bot.utils

    def get_player(self, ctx):
        player = self.players.get(ctx.guild.id)
        if player is None:
            player = AudioPlayer(ctx, self, self.nodes.get(self._nodes[0]["host"]))
            self.players[ctx.guild.id] = player

        return player

    async def get_tracks(self, player, search: str):
        async with self.session.get(f"http://{player.node.host}:2333/loadtracks?identifier={search}", headers={"Authorization": player.node.password}) as resp:
            tracks = await resp.json()
            return tracks
    
    async def on_socket_response(self, data):
        if data["t"] == "VOICE_SERVER_UPDATE":
            payload = {
                "op": "voiceUpdate",
                "guildId": data["d"]["guild_id"],
                "sessionId": self.bot.get_guild(int(data["d"]["guild_id"])).me.voice.session_id,
                "event": data["d"]
            }
            await self.nodes.get(self._nodes[0]["host"]).send(**payload)

    async def connect(self, ctx):
        await self.bot.ws.send(json.dumps({
            "op": 4,
            "d": {
                "guild_id": ctx.guild.id,
                "channel_id": ctx.author.voice.channel.id,
                "self_mute": False,
                "self_deaf": False
            }
        }))
        self.get_player(ctx).is_connected = True

    async def leave(self, ctx):
        await self.bot.ws.send(json.dumps({
            "op": 4,
            "d": {
                "guild_id": ctx.guild.id,
                "channel_id":  None,
                "self_mute": False,
                "self_deaf": False
            }
        }))
        try:
            del self.players[ctx.guild.id]
        except KeyError:
            pass
        
    async def audio_task(self):
        for i in range(len(self._nodes)):
            node = AudioNode(self, self.shards, self._nodes[i]["host"], self._nodes[i]["password"], self._nodes[i]["port"])
            await node.launch()
            self.nodes[node.host] = node
        self.bot.loop.create_task(self.node_event_task())

    async def node_event_task(self):

        for node in self.nodes.values():
            @node.ee.on("track_start")
            async def on_track_start(e):
                print("Music: track_start event triggered.")
                ctx = e.player.ctx
                #print(dir(e))
                f = e
                e = e.track
                #print(dir(e))
                em = discord.Embed(color=0x00ff00, title=f"Music")
                #em.description = f"**{e.track.title}**"
                em.set_author(name=e.requester.name, icon_url=e.requester.avatar_url)
                second = e.length / 1000
                minute, second = divmod(second, 60)
                hour, minute = divmod(minute, 60)
                #minutes, seconds = divmod(e.track.duration, 60)
                #em.add_field(name='Length', value=f"{str(minutes)}:{str(seconds).replace('0', '00').replace('1', '01').replace('2', '02').replace('3', '03').replace('4', '04').replace('5', '05').replace('6', '06').replace('7', '07').replace('8', '08').replace('9', '09')}")
                if hour:
                    length = f"{int(hour)}:{self.utils.format_time(minute)}:{self.utils.format_time(second)}"
                else:
                    length = f"{self.utils.format_time(minute)}:{self.utils.format_time(second)}"
                playing_panel = textwrap.dedent(f"""
I started playing the music! {self.bot.get_emoji(511089456196091916)}

:musical_note: **Song**
{e.title}

{self.bot.get_emoji(430340802879946773)} **Requested By**
{str(ctx.author)}

:timer: **Length**
{length}

:loud_sound: **Volume**
{f.player.volume}

:1234: **Queue Position**
{len(f.player.queue)}
                """)
                #em.add_field(name='Length', value=length)
                #em.add_field(name='Volume', value=f"{self.utils.get_lines(e.player.volume)} {e.player.volume}%")
                em.description = playing_panel
                #em.add_field(name='Position in Queue', value=len(e.player.queue))
                msg = await ctx.send(embed=em, edit=False)
                try:
                    await msg.add_reaction("\U000023f8") # Pause
                    await msg.add_reaction("\U000025b6") # Play/Resume
                    await msg.add_reaction("\U000023f9") # Stop
                    await msg.add_reaction("\U0001f501") # Repeat
                    await msg.add_reaction("\U00002753") # Help
                except discord.Forbidden:
                    return await ctx.send("I don't have Add Reaction permissions, so I can't show my awesome playing panel!")
                try:    
                    while f.player.playing:
                        if len(ctx.author.voice.channel.members) <= 1:
                            return await ctx.send(f"Guys? Seriously? Well, guess I'm out too. {self.bot.get_emoji(517142988904726562)}")
                        reaction, user = await self.bot.wait_for("reaction_add", check=lambda r, u: u.id == ctx.author.id and r.emoji in "⏸▶⏹🔁❓")
                        if reaction.emoji == "⏸":
                            await e.pause()
                            try:
                                await msg.remove_reaction("\U000023f8", user)
                            except: 
                                pass
                        elif reaction.emoji == "▶":
                            await e.resume()
                            await msg.remove_reaction("\U000025b6", user)
                        elif reaction.emoji == "⏹":
                            e.player.queue.clear()
                            await e.stop()
                            await msg.delete()
                        elif reaction.emoji == "🔁":
                            e.repeating = not e.repeating
                            await msg.remove_reaction("\U0001f501", user)
                        elif reaction.emoji == "❓":
                            await msg.remove_reaction("\U00002753", user)
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

            @node.ee.on("track_end")
            async def on_track_end(event):
                print("Music: track_end event triggered.")
                if event.reason == "REPLACED":
                    return  # Return because if we play then the queue will be fucked.
                elif event.reason == "FINISHED":
                    if event.player.repeating:
                        await event.player.node.send(op="play", guildId=str(event.player.ctx.guild.id), track=event.player.current.track)
                        return event.player.node.ee.emit("track_start", TrackStart(event.player, event.player.current))
                    await event.player.play()

            @node.ee.on("queue_concluded")
            async def on_queue_concluded(event):
                print("Music: queue_concluded event triggered.")
                await self.leave(event.player.ctx)
