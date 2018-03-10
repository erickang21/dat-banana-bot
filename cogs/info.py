import discord
import sys
import os
import io
import asyncio
import dbl
from discord.ext import commands


class Info:
    def __init__(self, bot):
        self.bot = bot
        with open('data/apikeys.json') as f:
            lol = json.load(f)
            self.token = lol.get("dbotsapi")


    @commands.command()
    async def stats(self, ctx):
        """Statsies for this bot. Be a nerd!"""       
        color = discord.Color(value=0x00ff00)
        em = discord.Embed(color=color, title='Bot Stats')
        em.description = "These are some stats for the lovely dat banana bot#0170."
        em.set_thumbnail(url="https://c1.staticflickr.com/6/5611/15804684456_0c2d30237d_z.jpg")        
        em.add_field(name='Creator', value='dat banana boi#1982')
        em.add_field(name='Devs', value='Free TNT#5796')
        em.add_field(name='Number of Servers', value=f'{len(self.bot.guilds)} servers') 
        em.add_field(name='Version', value='5.0.2 BETA')
        em.add_field(name='Start Date', value='12/08/2017')
        em.add_field(name='Bot Region', value='North America')
        em.add_field(name='Code Platform', value='Sublime Text')
        em.add_field(name='Hosting Platform', value='Amazon Web Services')
        em.add_field(name='Coding Language', value='Python, discord.py')      
        await ctx.send(embed=em)


    @commands.command()
    async def dbotinfo(self, ctx):
        """Gets stats for dat banana bot on Discord Bots."""
        color = discord.Color(value=0x00ff00)
        em = discord.Embed(color=color, title='Discord Bots')
        dblpy = dbl.Client(self.bot, self.token)
        em.add_field(name='Upvotes', value=await dblpy.get_upvote_count)

        
        

def setup(bot): 
    bot.add_cog(Info(bot)) 
