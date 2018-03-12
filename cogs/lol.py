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
        '''Gets a League of Legends summoner profile.'''
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


    @commands.command()
    async def lolchampmasteries(self, ctx, *, name=None):
        '''Gets champion masteries for an LoL summoner.'''
        try:
            await ctx.trigger_typing()
            client = talon.Client(token=self.token)
            summoner = await client.get_champion_mastery(region=None, query=name)
            em = discord.Embed(color=discord.Color(value=0x00ff00), title='LoL Champion Masteries')
            async with aiohttp.ClientSession() as session:
                async with session.get(f"https://na1.api.riotgames.com/lol/static-data/v3/champions/{summoner[0]['championId']}?locale=en_US&champData=all&api_key={self.token}") as resp:
                    resp = await resp.json()
                    em.add_field(name='Champion', value=resp['name'])
                    em.add_field(name='Level', value=f"{summoner[0]['championLevel']} ({summoner[0]['championPointsSinceLastLevel']}/{summoner[0]['championPointsUntilNextLevel']})")
                    if summoner[0]['chestGranted']:
                        cheststatus = 'Yes'
                    else:
                        cheststatus = 'No'
                    em.add_field(name='Total Points', value=summoner[0]['championPoints'])
                    em.add_field(name='Is chest granted?', value=cheststatus)
                    em.add_field(name='Tokens Earned', value=summoner[0]['tokensEarned'])
                    em.set_thumbnail(url=f"http://ddragon.leagueoflegends.com/cdn/6.24.1/img/champion/{resp['name'].replace(' ', '')}.png")
                    em.set_author(name=name)
                    await ctx.send(embed=em)
                    await ctx.trigger_typing()
                    client = talon.Client(token=self.token)
                    summoner = await client.get_champion_mastery(region=None, query=name)
                    em = discord.Embed(color=discord.Color(value=0x00ff00), title='LoL Champion Masteries')
                    async with aiohttp.ClientSession() as session:
                        async with session.get(f"https://na1.api.riotgames.com/lol/static-data/v3/champions/{summoner[1]['championId']}?locale=en_US&champData=all&api_key={self.token}") as resp:
                            resp = await resp.json()
                            em.add_field(name='Champion', value=resp['name'])
                            em.add_field(name='Level', value=f"{summoner[1]['championLevel']} ({summoner[1]['championPointsSinceLastLevel']}/{summoner[1]['championPointsUntilNextLevel']})")
                            if summoner[1]['chestGranted']:
                                cheststatus = 'Yes'
                            else:
                                cheststatus = 'No'
                            em.add_field(name='Total Points', value=summoner[1]['championPoints'])
                            em.add_field(name='Is chest granted?', value=cheststatus)
                            em.add_field(name='Tokens Earned', value=summoner[1]['tokensEarned'])
                            em.set_thumbnail(url=f"http://ddragon.leagueoflegends.com/cdn/6.24.1/img/champion/{resp['name'].replace(' ', '')}.png")
                            em.set_author(name=name)
                            await ctx.send(embed=em)
                            await ctx.trigger_typing()
                            client = talon.Client(token=self.token)
                            summoner = await client.get_champion_mastery(region=None, query=name)
                            em = discord.Embed(color=discord.Color(value=0x00ff00), title='LoL Champion Masteries')
                            async with aiohttp.ClientSession() as session:
                                async with session.get(f"https://na1.api.riotgames.com/lol/static-data/v3/champions/{summoner[2]['championId']}?locale=en_US&champData=all&api_key={self.token}") as resp:
                                    resp = await resp.json()
                                    em.add_field(name='Champion', value=resp['name'])
                                    em.add_field(name='Level', value=f"{summoner[2]['championLevel']} ({summoner[2]['championPointsSinceLastLevel']}/{summoner[2]['championPointsUntilNextLevel']})")
                                    if summoner[2]['chestGranted']:
                                        cheststatus = 'Yes'
                                    else:
                                        cheststatus = 'No'
                                    em.add_field(name='Total Points', value=summoner[2]['championPoints'])
                                    em.add_field(name='Is chest granted?', value=cheststatus)
                                    em.add_field(name='Tokens Earned', value=summoner[2]['tokensEarned'])
                                    em.set_thumbnail(url=f"http://ddragon.leagueoflegends.com/cdn/6.24.1/img/champion/{resp['name'].replace(' ', 'p')}.png")
                                    em.set_author(name=name)
                                    await ctx.send(embed=em)
        except KeyError as e:
            print(f"KeyError: {e}")
            await ctx.send("Error finding your profile. Maybe check the name?")
                    
                     



					

def setup(bot): 
    bot.add_cog(League_Of_Legends(bot))  


