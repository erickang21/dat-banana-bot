import discord
import sys
import os
import io
import asyncio
import psutil
import time
import textwrap
from discord.ext import commands


class Info:
    def __init__(self, bot):
        self.bot = bot
        self.starttime = self.bot.starttime



    @commands.command(aliases=['info', 'botinfo'])
    async def stats(self, ctx):
        """Statsies for this bot. Be a nerd!"""       
        color = discord.Color(value=0x00ff00)
        RAM = psutil.virtual_memory()
        used = RAM.used >> 20
        percent = RAM.percent
        member = 0
        for i in self.bot.guilds:
            for x in i.members:
                member += 1
        second = time.time() - self.starttime
        minute, second = divmod(second, 60)
        hour, minute = divmod(minute, 60)
        day, hour = divmod(hour, 24)
        em = discord.Embed(color=color, title='Bot Stats')
        em.description = "These are some stats for the lovely dat banana bot#0170."
        em.set_thumbnail(url="https://c1.staticflickr.com/6/5611/15804684456_0c2d30237d_z.jpg")        
        em.add_field(name='Creator', value=f'dat banana boi#1982 {self.bot.get_emoji(430848003180462114)}')
        em.add_field(name='Devs', value='Free TNT#5796')
        em.add_field(name='Servers :homes: ', value=f'{len(self.bot.guilds)}')
        em.add_field(name='Total Members :busts_in_silhouette: ', value=member)
        em.add_field(name='Connected Voice Channels :loud_sound: ', value=len(self.bot.voice_clients))  
        em.add_field(name='Latency :ping_pong: ', value=f"{self.bot.latency * 1000:.4f} ms")
        em.add_field(name='Version', value='7.0.3')
        em.add_field(name=f'Start Date {self.bot.get_emoji(430847593439035392)}', value='12/08/2017')
        em.add_field(name='Coding Language :computer: ', value=f'Python, discord.py {self.bot.get_emoji(418934774623764491)}') 
        em.add_field(name=f'Hosting Platform {self.bot.get_emoji(440698056346697728)}', value='Amazon Web Services') 
        em.add_field(name='Memory Usage', value=f"{used} MB ({percent}%)")
        em.add_field(name='Bot Uptime :clock:', value="%d days, %d hours, %d minutes, %d seconds" % (day, hour, minute, second)) 
        em.add_field(name='Commands Run (Since Uptime) :outbox_tray:', value=self.bot.commands_run)  
        em.add_field(name='Starboards', value=await self.bot.db.starboard.count())
        em.add_field(name='Saved CR Tags', value=await self.bot.db.crtags.count())
        em.add_field(name='Saved COC Tags', value=await self.bot.db.coctags.count())
        em.add_field(name='Active Mod Logs', value=await self.bot.db.modlog.count())
        await ctx.send(embed=em)



    @commands.command(aliases=['updates'])
    async def botupdates(self, ctx):
        """Read the latest notes on the latest update!"""    
        em = discord.Embed(color=discord.Color(
            value=0x00ff00), title='v7.0.3 > Fortnite')
        em.description = textwrap.dedent("""
        __**BIG STUFF**__
        -> :warning: Added NSFW commands. :warning: 
        -> CleverBot.io has been implemented! Have a siri-like thing on the bot! Talk to it today...
        -> Music loads a LOT faster and takes up less memory because of streaming!
        -> A **massive** buff to cocprofile. Sends in one neat message with emojis!

        __**Little-r Things**__
        -> Added Ruby and Lua to coliru languages. That's for you, TNT.
        -> No more gambling super lightning fast. 5 minute cooldown to it.
        -> Fixed a bug where: When the bot tries to remove music reactions but lacks permissions, the entire thing cuts off and stops.
        -> Buffed serverinfo a lot. You can now search the server info of other servers just by adding the name after the command! It can only see the servers that the bot is in, unfortunately.
        -> Buffed userinfo, now with server-specific stats for that user.

        """)
        await ctx.send(embed=em)

def setup(bot): 
    bot.add_cog(Info(bot)) 
