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


class League_Of_Legends:
    def __init__(self, bot):
        self.bot = bot
        with open('data/apikeys.json') as f:
            lol = json.load(f)
        self.token = lol.get("lolapi")
        

    def get_champion_by_id(self, champion: str):
        champs = {
            "1": "Annie",
            "2": "Olaf",
            "3": "Galio",
            "4": "Twisted Fate",
            "5": "Xin Zhao",
            "6": "Urgot",
            "7": "Leblanc",
            "8": "Vladimir",
            "9": "Fiddlesticks",
            "10": "Kayle",
            "11": "Master Yi",
            "12": "Alistar",
            "13": "Ryze",
            "14": "Sion",
            "15": "Sivir",
            "16": "Soraka",
            "17": "Teemo",
            "18": "Tristana",
            "19": "Warwick",
            "20": "Nunu",
            "21": "Miss Fortune",
            "22": "Ashe",
            "23": "Tryndamere",
            "24": "Jax",
            "25": "Morgana",
            "26": "Zilean",
            "27": "Singed",
            "28": "Evelynn",
            "29": "Twitch",
            "30": "Karthus",
            "31": "Chogath",
            "32": "Amumu",
            "33": "Rammus",
            "34": "Anivia",
            "35": "Shaco",
            "36": "Dr Mundo",
            "37": "Sona",
            "38": "Kassadin",
            "39": "Irelia",
            "40": "Janna",
            "41": "Gangplank",
            "42": "Corki",
            "43": "Karma",
            "44": "Taric",
            "45": "Veigar",
            "48": "Trundle",
            "50": "Swain",
            "51": "Caitlyn",
            "53": "Blitzcrank",
            "54": "Malphite",
            "55": "Katarina",
            "56": "Nocturne",
            "57": "Maokai",
            "58": "Renekton",
            "59": "Jarvan IV",
            "60": "Elise",
            "61": "Orianna",
            "62": "Wukong",
            "63": "Brand",
            "64": "LeeSin",
            "67": "Vayne",
            "68": "Rumble",
            "69": "Cassiopeia",
            "72": "Skarner",
            "74": "Heimerdinger",
            "75": "Nasus",
            "76": "Nidalee",
            "77": "Udyr",
            "78": "Poppy",
            "79": "Gragas",
            "80": "Pantheon",
            "81": "Ezreal",
            "82": "Mordekaiser",
            "83": "Yorick",
            "84": "Akali",
            "85": "Kennen",
            "86": "Garen",
            "89": "Leona",
            "90": "Malzahar",
            "91": "Talon",
            "92": "Riven",
            "96": "KogMaw",
            "98": "Shen",
            "99": "Lux",
            "101": "Xerath",
            "102": "Shyvana",
            "103": "Ahri",
            "104": "Graves",
            "105": "Fizz",
            "106": "Volibear",
            "107": "Rengar",
            "110": "Varus",
            "111": "Nautilus",
            "112": "Viktor",
            "113": "Sejuani",
            "114": "Fiora",
            "115": "Ziggs",
            "117": "Lulu",
            "119": "Draven",
            "120": "Hecarim",
            "121": "Khazix",
            "122": "Darius",
            "126": "Jayce",
            "127": "Lissandra",
            "131": "Diana",
            "133": "Quinn",
            "134": "Syndra",
            "136": "Aurelion Sol",
            "141": "Kayn",
            "142": "Zoe",
            "143": "Zyra",
            "145": "Kaisa",
            "150": "Gnar",
            "154": "Zac",
            "157": "Yasuo",
            "161": "Velkoz",
            "163": "Taliyah",
            "164": "Camille",
            "201": "Braum",
            "202": "Jhin",
            "203": "Kindred",
            "222": "Jinx",
            "223": "Tahm Kench",
            "236": "Lucian",
            "238": "Zed",
            "240": "Kled",
            "245": "Ekko",
            "254": "Vi",
            "266": "Aatrox",
            "267": "Nami",
            "268": "Azir",
            "412": "Thresh",
            "420": "Illaoi",
            "421": "RekSai",
            "427": "Ivern",
            "429": "Kalista",
            "432": "Bard",
            "497": "Rakan",
            "498": "Xayah",
            "516": "Ornn"
        }
        j = {}
        c = 0
        for i in champs.values():
            c += 1
            j[i] = str(c)
        try:
            return j[champion]
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
    async def champinfo(self, ctx, champion=None):
        try:
            champion = champion.strip("'")
            lol = self.get_champion_by_id(champion)
            if lol == 'Error':
                return await ctx.send("Can't find that specified champion. Note that champion names must be case-sensitive.")
            async with aiohttp.ClientSession() as session:
                async with session.get(f"https://na1.api.riotgames.com/lol/static-data/v3/champions/{lol}?locale=en_US&champData=all&tags=all&api_key={self.token}") as resp:
                    resp = await resp.json()
                    em = discord.Embed(color=discord.Color(value=0x00ff00), title=champion)
                    em.description = resp['lore']
                    em.add_field(name='Type', value=resp['tags'][0])
                    em.add_field(name='Health', value=f"{int(resp['stats']['hp'])} (+{int(resp['stats']['hpperlevel'])} per level")
                    em.add_field(name='Attack Damage', value=f"{int(resp['stats']['attackdamage'])} (+{int(resp['stats']['attackdamageperlevel'])} per level)")
                    em.add_field(name='Armor', value=f"{int(resp['stats']['armor'])} (+{int(resp['stats']['armorperlevel'])} per level)")
                    em.add_field(name='Health Regen', value=f"{int(resp['stats']['hpregen'])}/second (+{int(resp['stats']['hpregenperlevel'])} per level)")
                    skins = ''
                    for i in resp['skins']:
                        skins += i['name'].replace('default', champion)
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
        except Exception as e:
            print(f"Error: {e}")
            await ctx.send("An unknown error occurred. Details: {e}")


            


					

def setup(bot): 
    bot.add_cog(League_Of_Legends(bot))  


