import discord
import sys
import os
import io
import json
import aiohttp
import ezjson
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
   			async with aiohttp.ClientSession() as session:
			    async with session.get(f'https://na1.api.riotgames.com/lol/summoner/v3/summoners/by-name/{name}?api_key={self.token}') as resp:
			        resp = await resp.json()
			        color = discord.Color(value=0x00ff00)
			        em = discord.Embed(color=color, title=resp['name'])
			        em.add_field(name='Summoner Level', value=resp['summonerLevel'])
			        em.add_field(name='ID', value=resp['id'])
			        em.set_thumbnail(url=f"http://ddragon.leagueoflegends.com/cdn/6.24.1/img/profileicon/{resp['profileIconId']}.png")
			        await ctx.send(embed=em)
			        async with aiohttp.clientSession() as session:
			        	async with session.get(f"https://na1.api.riotgames.com//lol/champion-mastery/v3/champion-masteries/by-summoner/{resp['id']}?api_key={self.token}") as r:
                            r = await r.json()
                            color = discord.Color(value=0x00ff00)
                            em = discord.Embed(color=color, title='Champion Masteries')
                            async with aiohttp.ClientSession() as session:
								async with session.get(f'https://na1.api.riotgames.com/lol/static-data/v3/champions/{r[0]['championId']}?api_key={self.token}') as response:
									response = await response.json()
									em.add_field(name='Champion', value=response['name'])
									em.add_field(name='Level', value=r[0]['championLevel'])
									totalpoints = int(r[0]['championPointsSinceLastLevel']) + int(r[0]['championPointsUntilNextLevel'])
									em.add_field(name='Progress', value=f"{r[0]['championPointsSinceLastLevel']}/{totalpoints}")
									em.add_field(name='Total Points Earned', value=r[0]['championPoints'])
									em.add_field(name='Tokens Earned', value=r[0]['tokensEarned'])
									if r[0]['chestGranted'] is True:
										cheststatus = 'Granted'
									else:
										cheststatus = 'Not Granted'
									em.add_field(name='Chest Granted', value=cheststatus)
									async with aiohttp.ClientSession() as session:
										async with session.get(f'https://na1.api.riotgames.com/lol/static-data/v3/champions/{r[1]['championId']}?api_key={self.token}') as response:
											response = await response.json()
											em.add_field(name='Champion', value=response['name'])
									em.add_field(name='Level', value=r[1]['championLevel'])
									totalpoints = int(r[1]['championPointsSinceLastLevel']) + int(r[1]['championPointsUntilNextLevel'])
									em.add_field(name='Progress', value=f"{r[1]['championPointsSinceLastLevel']}/{totalpoints}")
									em.add_field(name='Total Points Earned', value=r[1]['championPoints'])
									em.add_field(name='Tokens Earned', value=r[1]['tokensEarned'])
									if r[1]['chestGranted'] is True:
										cheststatus = 'Granted'
									else:
										cheststatus = 'Not Granted'
									em.add_field(name='Chest Granted', value=cheststatus)
									async with aiohttp.ClientSession() as session:
										async with session.get(f'https://na1.api.riotgames.com/lol/static-data/v3/champions/{r[2]['championId']}?api_key={self.token}') as response:
											response = await response.json()
											em.add_field(name='Champion', value=response['name'])
									em.add_field(name='Level', value=r[2]['championLevel'])
									totalpoints = int(r[2]['championPointsSinceLastLevel']) + int(r[2]['championPointsUntilNextLevel'])
									em.add_field(name='Progress', value=f"{r[2]['championPointsSinceLastLevel']}/{totalpoints}")
									em.add_field(name='Total Points Earned', value=r[2]['championPoints'])
									em.add_field(name='Tokens Earned', value=r[2]['tokensEarned'])
									if r[2]['chestGranted'] is True:
										cheststatus = 'Granted'
									else:
										cheststatus = 'Not Granted'
									em.add_field(name='Chest Granted', value=cheststatus)
									await ctx.send(embed=em)

					

def setup(bot): 
    bot.add_cog(League_Of_Legends(bot))  


