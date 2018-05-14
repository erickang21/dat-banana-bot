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
        em.add_field(name='Version', value='7.0.1')
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
        em = discord.Embed(color=discord.Color(value=0x00ff00), title='v7.0.1 is READY TO ROLL!')
        em.description = textwrap.dedent("""
        -Completely revamped serverinfo with a load of new features, cuz that's what I'm for.
        
        -Mod logs now show deleted pictures, in case a ~~dirty pic~~ got deleted and you needed a reason to ban that person.
        
        -Userinfo now shows the user's playing status if there is one. Ez way to see if someone has a life or not.
        
        -Did your brain get a memory leak that caused you to forget your custom prefix? Ez, the bot mention now works as prefix too. @dat banana bot#0170 help!
        
        -Need to replicate the American elections? Use the *poll command to easily create a poll.
        *poll What is the question?|This is|Nothing is
        
        -Need to show off your coding skills but eval ain't for everyone? Use coliru to safely evaluate code!
        
        -Who's the **<3**'ers? Find out with the *ship command! 
        
        -**Finally patched the economy system, with gucci stuff to go!**
         -> Get ready to be addicted with the gamble command! Win it or loZE it!
        
        -**Starboard got a massive buff today!** The message will now edit if more/less stars are added to it. Good for your server members to see the popularity points instead of the bot sending 20 messages with the same message.

        **FIXED BUGS**   
        -Fixed serverinfo so it will send even if bot doesn't have Ban Members permission.
    
        -Counters for COC/CR tags, starboard, modlogs etc in the *stats would show 0 because I screwed something up.

        """)
        await ctx.send(embed=em)

def setup(bot): 
    bot.add_cog(Info(bot)) 
