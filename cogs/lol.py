import discord
import sys
import os
import io
import json
import aiohttp
import ezjson
import talon
import random
from discord.ext import commands


class lol:
    def __init__(self, bot):
        self.bot = bot
        with open('data/apikeys.json') as f:
            lol = json.load(f)
        self.token = lol.get("lolapi")
        

    def get_champion_by_id(self, champion: str):
        f = open("data/loldata.json").read()
        x = json.loads(f)
        try:
            return x['data'][champion]['key']
        except KeyError:
            return 'Error'


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


    @commands.command(aliases=['lolcm', 'lolmastery'])
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
                    if resp['name'] == 'Wukong':
                        champname = 'MonkeyKing'
                    else:
                        champname = resp['name'].replace(' ', '')
                    em.set_thumbnail(url=f"http://ddragon.leagueoflegends.com/cdn/6.24.1/img/champion/{champname}.png")
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
                            if resp['name'] == 'Wukong':
                                champname = 'MonkeyKing'
                            else:
                                champname = resp['name'].replace(' ', '')
                            em.set_thumbnail(url=f"http://ddragon.leagueoflegends.com/cdn/6.24.1/img/champion/{champname}.png")
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
                                    if resp['name'] == 'Wukong':
                                        champname = 'MonkeyKing'
                                    else:
                                        champname = resp['name'].replace(' ', '')
                                    em.set_thumbnail(url=f"http://ddragon.leagueoflegends.com/cdn/6.24.1/img/champion/{champname}.png")
                                    em.set_author(name=name)
                                    await ctx.send(embed=em)
        except KeyError as e:
            print(f"KeyError: {e}")
            await ctx.send("Error finding your profile. Maybe check the name?")
                    
                     

    @commands.command()
    async def champinfo(self, ctx, *, champion=None):
        try:
            await ctx.trigger_typing()
            champion = champion.strip("'")
            lol = self.get_champion_by_id(champion)
            if lol == 'Error':
                return await ctx.send("Can't find that specified champion. Note that champion names must be case-sensitive.")
            async with aiohttp.ClientSession() as session:
                async with session.get(f"https://na1.api.riotgames.com/lol/static-data/v3/champions/{lol}?locale=en_US&champData=all&tags=all&api_key={self.token}") as resp:
                    resp = await resp.json()
                    em = discord.Embed(color=discord.Color(value=0x00ff00), title=resp['name'])
                    em.description = resp['lore']
                    em.add_field(name='Type', value=resp['tags'][0])
                    em.add_field(name='Health', value=f"{int(resp['stats']['hp'])} (+{int(resp['stats']['hpperlevel'])} per level)")
                    em.add_field(name='Attack Damage', value=f"{int(resp['stats']['attackdamage'])} (+{int(resp['stats']['attackdamageperlevel'])} per level)")
                    em.add_field(name='Armor', value=f"{int(resp['stats']['armor'])} (+{int(resp['stats']['armorperlevel'])} per level)")
                    em.add_field(name='Health Regen', value=f"{int(resp['stats']['hpregen'])}/second (+{int(resp['stats']['hpregenperlevel'])} per level)")
                    skins = ''
                    for i in resp['skins']:
                        skins += f"{i['name'].replace('default', champion)} \n"
                    em.add_field(name='Skins', value=skins)
                    em.add_field(name=f'A tip to use {champion}', value=resp['allytips'][random.randint(0, 2)])
                    em.add_field(name=f'A tip against {champion}', value=resp['enemytips'][random.randint(0, 2)])
                    em.set_author(name=resp['title'])
                    if resp['name'] == 'Wukong':
                        champname = 'MonkeyKing'
                    else:
                        champname = resp['name'].replace(' ', '')
                        champname = champname.strip("'")
                    em.set_thumbnail(url=f"http://ddragon.leagueoflegends.com/cdn/6.24.1/img/champion/{champname}.png")
                    await ctx.send(embed=em)
                    await ctx.trigger_typing()
                    em = discord.Embed(color=discord.Color(value=0x00ff00), title=f"Recommended set for: {resp['name']}")
                    em.description = "Summoner's Rift"
                    async with aiohttp.ClientSession() as session:
                        async with session.get(f"https://na1.api.riotgames.com/lol/static-data/v3/items/{resp['recommended'][0]['blocks'][0]['items'][0]['id']}locale=en_US&tags=all&itemData=all&api_key={self.token}") as r:
                            r = await r.json()
                            async with aiohttp.ClientSession() as session:
                                async with session.get(f"https://na1.api.riotgames.com/lol/static-data/v3/items/{resp['recommended'][0]['blocks'][0]['items'][1]['id']}locale=en_US&tags=all&itemData=all&api_key={self.token}") as re:
                                    re = await re.json()
                                    em.add_field(name=r['blocks'][0]['type'].replace('_', ' '), value=f"{r['name']}({r['gold']['total']} Gold) \nDescription: {r['plaintext']}\nFeatures: {r['sanitizedDescription']} \n\n{re['name']}({re['gold']['total']} Gold) \nDescription: {re['plaintext']}\nFeatures: {re['sanitizedDescription']}")
                                    async with aiohttp.ClientSession() as session:
                                        async with session.get(f"https://na1.api.riotgames.com/lol/static-data/v3/items/{resp['recommended'][0]['blocks'][1]['items'][0]['id']}locale=en_US&tags=all&itemData=all&api_key={self.token}") as r:
                                            r = await r.json()
                                            async with aiohttp.ClientSession() as session:
                                                async with session.get(f"https://na1.api.riotgames.com/lol/static-data/v3/items/{resp['recommended'][0]['blocks'][1]['items'][1]['id']}locale=en_US&tags=all&itemData=all&api_key={self.token}") as re:
                                                    re = await re.json()
                                                    em.add_field(name=r['blocks'][0]['type'].replace('_', ' '), value=f"{r['name']}({r['gold']['total']} Gold) \nDescription: {r['plaintext']}\nFeatures: {r['sanitizedDescription']} \n\n{re['name']}({re['gold']['total']} Gold) \nDescription: {re['plaintext']}\nFeatures: {re['sanitizedDescription']}")
                                                    async with aiohttp.ClientSession() as session:
                                                        async with session.get(f"https://na1.api.riotgames.com/lol/static-data/v3/items/{resp['recommended'][0]['blocks'][2]['items'][0]['id']}locale=en_US&tags=all&itemData=all&api_key={self.token}") as r:
                                                            r = await r.json()
                                                            async with aiohttp.ClientSession() as session:
                                                                async with session.get(f"https://na1.api.riotgames.com/lol/static-data/v3/items/{resp['recommended'][0]['blocks'][2]['items'][1]['id']}locale=en_US&tags=all&itemData=all&api_key={self.token}") as re:
                                                                    re = await re.json()
                                                                    em.add_field(name=r['blocks'][0]['type'].replace('_', ' '), value=f"{r['name']}({r['gold']['total']} Gold) \nDescription: {r['plaintext']}\nFeatures: {r['sanitizedDescription']} \n\n{re['name']}({re['gold']['total']} Gold) \nDescription: {re['plaintext']}\nFeatures: {re['sanitizedDescription']}")
                                                                    await ctx.send(embed=em)
        except Exception as e:
            print(f"Error: {e}")
            await ctx.send(f"An unknown error occurred. Details: {e}")


            


					

def setup(bot):  
    bot.add_cog(lol(bot))  


