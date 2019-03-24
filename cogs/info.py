import discord
import sys
import os
import io
import asyncio
import psutil
import time
import re
import textwrap
from discord.ext import commands


class Info:
    def __init__(self, bot):
        self.bot = bot
        self.starttime = self.bot.starttime
        


    @commands.command(aliases=['info', 'botinfo'])
    async def stats(self, ctx):
        """Statsies for this bot. Be a nerd!"""       
        color = 0xf9e236
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
        lol = subprocess.run(f"python -V", cwd='/Users/Administrator/new-banana-bot', stderr=subprocess.PIPE, stdout=subprocess.PIPE, shell=True)
        err = lol.stderr.decode("utf-8")
        res = lol.stdout.decode("utf-8")
        #content = (await self.bot.get_channel(392464990658887681).history(limit=1).flatten())[0].content
        #version = re.findall(r"v(\d.\d.\d)", content)[0]
        em = discord.Embed(color=color, title='Bot Stats')
        em.set_thumbnail(url=self.bot.user.avatar_url)        
        em.add_field(name='Creator', value=f'dat banana boi#5627')
        em.add_field(name='Devs', value='PoLLeN#5796')
        em.add_field(name='Servers :homes: ', value=f'{len(self.bot.guilds)}')
        em.add_field(name='Total Members :busts_in_silhouette: ', value=member)
        em.add_field(name='Connected Voice Channels :loud_sound: ', value=len(self.bot.voice_clients))  
        em.add_field(name='Latency :ping_pong: ', value=f"{self.bot.latency * 1000:.4f} ms")
        #em.add_field(name='Version', value=version)
        em.add_field(name=f'Start Date :calendar:', value='12/08/2017')
        em.add_field(name='Coding Language :computer: ', value=res) 
        em.add_field(name=f'Hosting Platform {self.bot.get_emoji(440698056346697728)}', value='Digital Ocean') 
        em.add_field(name='Memory Usage', value=f"{used} MB ({percent}%)")
        em.add_field(name='Bot Uptime :clock:', value="%d days, %d hours, %d minutes, %d seconds" % (day, hour, minute, second)) 
        em.add_field(name='Commands Run (Since Uptime) :outbox_tray:', value=self.bot.commands_run)  
        await ctx.send(embed=em)

    @commands.command()
    async def dbstats(self, ctx):
        names = await bot.db.collection_names()
        db_stuff = "**Database: MongoDB**\n\n"
        for name in names:
            count = await getattr(self.bot.db, name).count() 
            db_stuff += f"**{name}:** {count} entries\n"
        em = discord.Embed(color=ctx.author.color, title="Database Stats")
        em.description = db_stuff
        em.set_footer(text=f"Requested by: {src(ctx.author)}", icon_url=ctx.author.avatar_url)
        await ctx.send(embed=em)

    # @commands.command(aliases=['updates', 'bu', 'botu'])
    # async def botupdates(self, ctx):
    #     """Read the latest notes on the latest update!"""    
    #     content = (await self.bot.get_channel(392464990658887681).history(limit=1).flatten())[0].content
    #     title = content.split("\n")[0].replace("*", "")
    #     em = discord.Embed(color=discord.Color(value=0xf9e236))
    #     em.description = content
    #     await ctx.send(embed=em)

def setup(bot): 
    bot.add_cog(Info(bot)) 
