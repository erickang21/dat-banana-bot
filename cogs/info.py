import discord
import sys
import os
import io
import asyncio
from discord.ext import commands


class Info:
    def __init__(self, bot):
        self.bot = bot



    @commands.command(aliases=['info', 'botinfo'])
    async def stats(self, ctx):
        """Statsies for this bot. Be a nerd!"""       
        color = discord.Color(value=0x00ff00)
        em = discord.Embed(color=color, title='Bot Stats')
        em.description = "These are some stats for the lovely dat banana bot#0170."
        em.set_thumbnail(url="https://c1.staticflickr.com/6/5611/15804684456_0c2d30237d_z.jpg")        
        em.add_field(name='Creator', value='dat banana boi#1982')
        em.add_field(name='Devs', value='Free TNT#5796')
        em.add_field(name='Number of Servers', value=f'{len(self.bot.guilds)} servers') 
        em.add_field(name='Version', value='6.0.3')
        em.add_field(name='Start Date', value='12/08/2017')
        em.add_field(name='Bot Region', value='North America')
        em.add_field(name='Code Platform', value='VS Code/GitHub')
        em.add_field(name='Hosting Platform', value='Amazon Web Services')
        em.add_field(name='Coding Language', value='Python, discord.py')      
        await ctx.send(embed=em)



        
        

def setup(bot): 
    bot.add_cog(Info(bot)) 
