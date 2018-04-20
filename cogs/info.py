import discord
import sys
import os
import io
import asyncio
import psutil
import time
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
        em.add_field(name='Creator', value='dat banana boi#1982')
        em.add_field(name='Devs', value='Free TNT#5796')
        em.add_field(name='Servers', value=f'{len(self.bot.guilds)}') 
        em.add_field(name='Total Members', value=member)
        em.add_field(name='Connected Voice Channels', value=len(self.bot.voice_clients))  
        em.add_field(name='Latency', value=f"{self.bot.latency * 1000:.4f} ms")
        em.add_field(name='Version', value='6.0.6')
        em.add_field(name='Start Date', value='12/08/2017')
        em.add_field(name='Coding Language', value='Python, discord.py')  
        em.add_field(name='Memory Usage', value=f"{used} MB ({percent}%)")
        em.add_field(name='Bot Uptime', value="%d days, %d hours, %d minutes, %d seconds" % (day, hour, minute, second))    
        await ctx.send(embed=em)



        
        

def setup(bot): 
    bot.add_cog(Info(bot)) 
