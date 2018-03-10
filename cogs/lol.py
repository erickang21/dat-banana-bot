import discord
import sys
import os
import io
import json
import aiohttp
import ezjson
import talon
from discord.ext import commands


class League_Of_Legends:
    def __init__(self, bot):
        self.bot = bot
        with open('data/apikeys.json') as f:
            lol = json.load(f)
        self.token = lol.get("lolapi")
        

    @commands.command()
    async def lolprofile(self, ctx, *, name=None):
   		if name is None:
   			await ctx.send("Oops! Enter your summoner name like this: `*lolprofile [summoner name]`")
   		else:
            try:
                client = talon.Client(token=self.token)
                summoner = await client.get_summoner(query=name)
                em = discord.Embed(color=discord.Color(value=0x00ff00), title='LoL Profile')
                em.add_field(name='Summoner Level', value=summoner.summonerLevel)
                em.add_field(name='ID', value=summoner.id)
                em.set_author(name=name)
                em.set_thumbnail(url=f"http://ddragon.leagueoflegends.com/cdn/6.24.1/img/profileicon/{summoner.profileIconId}.png")
                await ctx.send(embed=em)
			except KeyError as e:
				print(f"KeyError: {e}")
                await ctx.send("Error finding your profile. Maybe check your name?")

					

def setup(bot): 
    bot.add_cog(League_Of_Legends(bot))  


