import discord
import sys
import os
import io
import json
import aiohttp
import ezjson
import urllib.parse
from discord.ext import commands


class COC:
    def __init__(self, bot):
        self.bot = bot
        self.session = self.bot.session
        with open('data/apikeys.json') as f:
            lol = json.load(f)
            self.token = lol.get("cocapi")
        self.client = {'Authorization': self.token}


    async def get_tag(self, id):
        '''Gets a COC tag by user ID.'''
        x = await self.bot.db.coctags.find_one({"id": str(id)})
        return x['tag'] if x is not None else None


    def emoji(self, name):
        with open('data/emojis.json') as f:
            lol = json.loads(f.read())
        e = lol[name]
        emo = self.bot.get_emoji(int(e))
        return emo if emo is not None else None



    @commands.command()
    async def cocsave(self, ctx, coctag):
        '''Saves a Clash of Clans tag to your Discord account.'''
        coctag = coctag.strip('#').replace("O", "0")
        coctag = coctag.upper()
        for char in coctag:
            if char.upper() not in '0289PYLQGRJCUV':
                return await ctx.send(f'Oops again! Looks like your tag `#{coctag}` is not a valid tag!')
        await self.bot.db.coctags.update_one({"id": str(ctx.author.id)}, {"$set": {"tag": coctag}}, upsert=True)
        await ctx.send("Success. :white_check_mark: Your tag is now saved to your account.")



    @commands.command()
    async def cocprofile(self, ctx, coctag=None):
        '''Gets a Clash of Clans profile! Yay!'''
        if coctag is None:
            coctag = await self.get_tag(ctx.author.id)
            if not coctag:
                return await ctx.send("Oops, looks like you don't have a saved tag yet! Use `*cocsave [tag]` to save your tag to your Discord profile.")              
            coctag = coctag.strip('#').replace("O", "0")
            coctag = coctag.upper()
        else:
            coctag = coctag.strip('#').replace("O", "0")
            coctag = coctag.upper()
        resp = await self.session.get(f'https://api.clashofclans.com/v1/players/%23{coctag}', headers=self.client)
        resp = await resp.json()
        color = discord.Color(value=0xe5f442)
        em = discord.Embed(color=color, title=f"{resp['name']}, {resp['tag']}")
        em.add_field(name="Home Base", value=self.emoji(f"th{resp['townHallLevel']}"), inline=False)
        em.add_field(name='XP Level', value=resp['expLevel'])
        em.add_field(name='Trophies', value=resp['trophies'])
        try:
            leaguename = resp['league']['name']
        except KeyError:
            leaguename = 'Unranked'
        em.add_field(name='League', value=leaguename)
        em.add_field(name='Best Trophies', value=resp['bestTrophies'])
        em.add_field(name='Town Hall', value=resp['townHallLevel'])
        em.add_field(name='Attack Wins', value=resp['attackWins'])
        em.add_field(name='Defense Wins', value=resp['defenseWins'])
        em.add_field(name='Donations', value=resp['donations'])
        em.add_field(name='Donations Received', value=resp['donationsReceived'])
        em.add_field(name='War Stars', value=resp['warStars'])
        try:
            em.set_thumbnail(url=resp['league']['iconUrls']['medium'])
        except KeyError:
            em.set_thumbnail(url='http://clash-wiki.com/images/progress/leagues/no_league.png')
        em.add_field(name="Builder Base", value=self.emoji(f"bh{resp['builderHallLevel']}"), inline=False)
        try:
            em.add_field(name='Builder Hall', value=resp['builderHallLevel'])
            em.add_field(name='Trophies', value=resp['versusTrophies'])
            em.add_field(name='Personal Best', value=resp['bestVersusTrophies'])
            em.add_field(name='Attack Wins', value=resp['versusBattleWins'])
        except KeyError:
            em.add_field(name="Builder Hall", value='Builder Base is not unlocked yet! Hit Town Hall 4 to unlock.')
        try:
            em.add_field(name="Clan", value=f"{resp['clan']['name']}, {resp['clan']['tag']}", inline=False)
            em.add_field(name='Clan Level', value=resp['clan']['clanLevel'])                            
            types = {
                'member': 'Member',
                'admin': 'Elder',
                'coLeader': 'Co-Leader',
                'leader': 'Leader'
            }
            em.add_field(name='Clan Role', value=types[resp['role']])
            em.set_author(name='Clan Info')
            em.set_thumbnail(url=resp['clan']['badgeUrls']['medium'])
        except KeyError:
            em.add_field(name="Clan", value=f"No Clan", inline=False)
        await ctx.send(embed=em)
        # else:
        #     coctag = coctag.strip('#')
        #     coctag = coctag.upper()
        #     resp = await self.session.get(f'https://api.clashofclans.com/v1/players/%23{coctag}', headers=self.client)
        #     resp = await resp.json()
        #     color = discord.Color(value=0xe5f442)
        #     em = discord.Embed(color=color, title=f"{resp['name']}, #{resp['tag']}")
        #     em.add_field(name='XP Level', value=resp['expLevel'])
        #     em.add_field(name='Trophies', value=resp['trophies'])
        #     try:
        #         leaguename = resp['league']['name']
        #     except KeyError:
        #         leaguename = 'Unranked'
        #     em.add_field(name='League', value=leaguename)
        #     em.add_field(name='Best Trophies', value=resp['bestTrophies'])
        #     em.add_field(name='Town Hall', value=resp['townHallLevel'])
        #     em.add_field(name='Attack Wins', value=resp['attackWins'])
        #     em.add_field(name='Defense Wins', value=resp['defenseWins'])
        #     em.add_field(name='Donations', value=resp['donations'])
        #     em.add_field(name='Donations Received', value=resp['donationsReceived'])
        #     em.add_field(name='War Stars', value=resp['warStars'])
        #     try:
        #         em.set_thumbnail(url=resp['league']['iconUrls']['medium'])
        #     except KeyError:
        #         em.set_thumbnail(url='http://clash-wiki.com/images/progress/leagues/no_league.png')
        #     em.set_author(name='Normal Base')
        #     await ctx.send(embed=em)
        #     try:
        #         em = discord.Embed(color=discord.Color(value=0xe5f442))
        #         em.add_field(name='Builder Hall', value=resp['builderHallLevel'])
        #         em.add_field(name='Trophies', value=resp['versusTrophies'])
        #         em.add_field(name='Personal Best', value=resp['bestVersusTrophies'])
        #         em.add_field(name='Attack Wins', value=resp['versusBattleWins'])
        #         em.set_author(name='Builder Base')
        #         await ctx.send(embed=em)
        #     except KeyError:
        #         em = discord.Embed(color=discord.Color(value=0xe5f442))
        #         em.description = 'Builder Base is not unlocked yet! Hit Town Hall 4 to unlock.'
        #         em.set_author(name='Builder Base')
        #         await ctx.send(embed=em)
        #     color = discord.Color(value=0xe5f442)
        #     try:
        #         em = discord.Embed(color=color, title=f"{resp['clan']['name']}, {resp['clan']['tag']}")
        #         em.add_field(name='Clan Level', value=resp['clan']['clanLevel'])                            
        #         types = {
        #             'member': 'Member',
        #             'admin': 'Elder',
        #             'coLeader': 'Co-Leader',
        #             'leader': 'Leader'
        #         }
        #         em.add_field(name='Clan Role', value=types[resp['role']])
        #         em.set_author(name='Clan Info')
        #         em.set_thumbnail(url=resp['clan']['badgeUrls']['medium'])
        #         await ctx.send(embed=em)
        #     except KeyError:
        #         em = discord.Embed(color=color, title="No Clan")
        #         em.set_thumbnail(url='http://i1253.photobucket.com/albums/hh599/bananaboy21/maxresdefault_zpseuid4jln.jpg')
        #         await ctx.send(embed=em)


    @commands.command()
    async def cocclan(self, ctx, clantag=None):
        """Gets clan info for a Clash of Clans clan."""
        if clantag is None:
            coctag = await self.get_tag(ctx.author.id)
            if not coctag:
                return await ctx.send("Oops, looks like you don't have a saved tag yet! Use `*cocsave [tag]` to save your tag to your Discord profile.")
            resp = await self.session.get(f'https://api.clashofclans.com/v1/players/%23{coctag}', headers=self.client)
            resp = await resp.json()
            try:
                clantag = resp['clan']['tag']
                clantag = clantag.strip('#')
            except KeyError:
                return await ctx.send("Oops! You aren't in a clan yet. \nTo search for a clan by clan tag, use `*cocclan [clan tag]`.")
            respclan = await self.session.get(f'https://api.clashofclans.com/v1/clans/%23{clantag}', headers=self.client)
            clan = await respclan.json()
            color = discord.Color(value=0xe5f442)
            em = discord.Embed(color=color, title='Clan Info')
            em.add_field(name='Location', value=clan.get('location', {}).get('name'))
            em.add_field(name='Clan Level', value=clan.get('clanLevel', 1))
            em.add_field(name='Clan Points - Home Base', value=clan.get('clanPoints', 0))
            em.add_field(name='Clan Points - Builder Base', value=clan.get('clanVersusPoints', 0))
            clanmembers = clan.get('members', 0)
            em.add_field(name='Members', value=f'{clanmembers}/50')
            em.add_field(name='Required Trophies', value=clan.get('requiredTrophies', 0))
            em.add_field(name='War Frequency', value=clan.get('warFrequency', 0))
            em.add_field(name='War Win Streak', value=clan.get('warWinStreak', 0))
            em.add_field(name='War Wins', value=clan.get('warWins', 0))
            em.add_field(name='War Draws', value=clan.get('warTies', 0))
            em.add_field(name='War Losses', value=clan.get('warLosses', 0))
            if clan['isWarLogPublic'] is True:
                warlog = 'Public'
            else:
                warlog = 'Private'
            em.add_field(name='War Log', value=warlog)
            em.set_author(name=f"{clan.get('name', '[Unknown Name]')} ({clan.get('tag', '[Unknown Tag]')})")
            em.set_thumbnail(url=clan['badgeUrls']['medium'])
            await ctx.send(embed=em)
        else:
            clantag = clantag.strip('#')
            clantag = clantag.upper()
            respclan = await self.session.get(f'https://api.clashofclans.com/v1/clans/%23{clantag}', headers=self.client)
            clan = await respclan.json()
            color = discord.Color(value=0xe5f442)
            em = discord.Embed(color=color, title='Clan Info')
            em.add_field(name='Location', value=clan.get('location', {}).get('name'))
            em.add_field(name='Clan Level', value=clan.get('clanLevel', 0))
            em.add_field(name='Clan Points - Home Base', value=clan.get('clanPoints', 0))
            em.add_field(name='Clan Points - Builder Base', value=clan.get('clanVersusPoints', 0))
            clanmembers = clan.get('members', 0)
            em.add_field(name='Members', value=f'{clanmembers}/50')
            em.add_field(name='Required Trophies', value=clan.get('requiredTrophies', 0))
            em.add_field(name='War Frequency', value=clan.get('warFrequency', 0))
            em.add_field(name='War Win Streak', value=clan.get('warWinStreak', 0))
            em.add_field(name='War Wins', value=clan.get('warWins', 0))
            em.add_field(name='War Draws', value=clan.get('warTies', 0))
            em.add_field(name='War Losses', value=clan.get('warLosses', 0))
            if clan['isWarLogPublic'] is True:
                warlog = 'Public'
            else:
                warlog = 'Private'
            em.add_field(name='War Log', value=warlog)
            em.set_author(name=f"{clan.get('name', '[Unknown Name]')} ({clan.get('tag', '[Unknown Tag]')})")
            em.set_thumbnail(url=clan['badgeUrls']['medium'])
            await ctx.send(embed=em)

    @commands.command()
    async def cocwar(self, ctx, clantag=None):
        if clantag is None:
            coctag = await self.get_tag(ctx.author.id)
            if not coctag:
                return await ctx.send("Oops, looks like you don't have a saved tag yet! Use `*cocsave [tag]` to save your tag to your Discord profile.")
            resp = await self.session.get(f'https://api.clashofclans.com/v1/players/%23{coctag}', headers=self.client) 
            resp = await resp.json()
            try:
                clantag = resp['clan']['tag']
                clantag = clantag.strip('#')
                clantag = clantag.upper()
            except KeyError:
                return await ctx.send("Oops! You aren't in a clan yet. \nTo search for a clan by clan tag, use `*cocclan [clan tag]`.")
            respclan = await self.session.get(f'https://api.clashofclans.com/v1/clans/%23{clantag}/currentwar', headers=self.client)
            clan = await respclan.json()
            color = discord.Color(value=0xe5f442)
            em = discord.Embed(color=color, title='War Info')
            em.description = f"{clan['clan']['stars']} :star: **vs** {clan['opponent']['stars']} :star:\n\n{clan['clan']['attacks']} attacks :crossed_swords: **vs** {clan['clan']['attacks']} attacks :crossed_swords:"
            try:
                teamsize = clan['teamSize']
                em.add_field(name='War Size', value=f'{teamsize} vs {teamsize}')
                em.add_field(name='Ally Clan Level', value=clan['clan']['clanLevel'])
                em.add_field(name='Enemy Clan Level', value=clan['opponent']['clanLevel'])
                em.set_author(name=f"{clan['clan']['name']}({clan['clan']['tag']}) vs {clan['opponent']['name']} ({clan['opponent']['tag']})")
                em.set_thumbnail(url=clan['clan']['badgeUrls']['medium'])
                await ctx.send(embed=em)
            except KeyError as e:
                print(e)
                color = discord.Color(value=0xf44e42)
                em = discord.Embed(color=color, title='Error')
                em.description = "This error happened for one of the following reasons: \n\n1) The clan is not currently in war.\n2) The clan's war log is set to Private.\n3) The given clan tag is invalid."
                await ctx.send(embed=em)
        else:
            clantag = clantag.strip('#')
            clantag = clantag.upper()
            respclan = await self.session.get(f'https://api.clashofclans.com/v1/clans/%23{clantag}/currentwar', headers=self.client)
            clan = await respclan.json()
            color = discord.Color(value=0xe5f442)
            em = discord.Embed(color=color, title='War Info')
            em.description = f"{clan['clan']['stars']} :star: **vs** {clan['opponent']['stars']} :star:\n\n{clan['clan']['attacks']} attacks :crossed_swords: **vs** {clan['clan']['attacks']} attacks :crossed_swords:"
            try:
                teamsize = clan['teamSize']
                em.add_field(name='War Size', value=f'{teamsize} vs {teamsize}')
                em.add_field(name='Ally Clan Level', value=clan['clan']['clanLevel'])
                em.add_field(name='Enemy Clan Level', value=clan['opponent']['clanLevel'])
                em.set_author(name=f"{clan['clan']['name']}({clan['clan']['tag']}) vs {clan['opponent']['name']} ({clan['opponent']['tag']})")
                em.set_thumbnail(url=clan['clan']['badgeUrls']['medium'])
                await ctx.send(embed=em)
            except KeyError as e:
                print(f"KeyError: {e}")
                color = discord.Color(value=0xf44e42)
                em = discord.Embed(color=color, title='Error')
                em.description = "This error happened for one of the following reasons: \n\n1) The clan is not currently in war.\n2) The clan's war log is set to Private.\n3) The given clan tag is invalid."
                await ctx.send(embed=em)


    @commands.command(aliases=['coccs', 'cocclans'])
    async def cocclansearch(self, ctx, *, clanname):
        '''Search for COC clans by name.'''
        try:
            em = discord.Embed(color=discord.Color(value=0x00ff00), title='Searching the COC Universe...')
            em.description = 'Hang tight! :mag:'
            msg = await ctx.send(embed=em)
            em = discord.Embed(color=discord.Color(value=0x00ff00), title=f"Search Results for: {clanname}")
            clanname = urllib.parse.quote(clanname)
            resp = await self.session.get(f'https://api.clashofclans.com/v1/clans?name={clanname}', headers=self.client) 
            resp = await resp.json()
            clantype = {
                "open": "Open",
                "inviteOnly": "Invite Only",
                "closed": "Closed"
            }
            wartype = {
                "always": "Always",
                "moreThanOncePerWeek": "More Than Once Per Week",
                "oncePerWeek": "Once Per Week",
                "lessThanOncePerWeek": "Less Than Once Per Week",
                "never": "Never",
                "unknown": "Unknown"
            }
            em.description = f"***Top 3 Results:***\n\n\n**{resp['items'][0]['name']} ({resp['items'][0]['tag']})**\nMembers: {resp['items'][0]['members']}/50\nStatus: {clantype[resp['items'][0]['type']]}\nLocation: {resp['items'][0]['location']['name']}\nClan Level: {resp['items'][0]['clanLevel']}\nClan Points:\n  ->Home Base: {resp['items'][0]['clanPoints']}\n  ->Builder Base:{resp['items'][0]['clanVersusPoints']}\nRequired Trophies: {resp['items'][0]['requiredTrophies']}\nWar Frequency: {wartype[resp['items'][0]['warFrequency']]}\nWar Win Streak: {resp['items'][0]['warWinStreak']}\n\n**{resp['items'][1]['name']} ({resp['items'][1]['tag']})**\nMembers: {resp['items'][1]['members']}/50\nStatus: {clantype[resp['items'][1]['type']]}\nLocation: {resp['items'][1]['location']['name']}\nClan Level: {resp['items'][1]['clanLevel']}\nClan Points:\n  ->Home Base: {resp['items'][1]['clanPoints']}\n  ->Builder Base:{resp['items'][1]['clanVersusPoints']}\nRequired Trophies: {resp['items'][1]['requiredTrophies']}\nWar Frequency: {wartype[resp['items'][1]['warFrequency']]}\nWar Win Streak: {resp['items'][1]['warWinStreak']}\n\n**{resp['items'][2]['name']} ({resp['items'][2]['tag']})**\nMembers: {resp['items'][2]['members']}/50\nStatus: {clantype[resp['items'][2]['type']]}\nLocation: {resp['items'][2]['location']['name']}\nClan Level: {resp['items'][2]['clanLevel']}\nClan Points:\n  ->Home Base: {resp['items'][2]['clanPoints']}\n  ->Builder Base:{resp['items'][2]['clanVersusPoints']}\nRequired Trophies: {resp['items'][2]['requiredTrophies']}\nWar Frequency: {wartype[resp['items'][2]['warFrequency']]}\nWar Win Streak: {resp['items'][2]['warWinStreak']}\n\n\n***See Also:***\n\n{resp['items'][3]['name']} ({resp['items'][3]['tag']}) \n{resp['items'][4]['name']} ({resp['items'][4]['tag']})\n{resp['items'][5]['name']} ({resp['items'][5]['tag']})\n{resp['items'][6]['name']} ({resp['items'][6]['tag']})"
            em.set_footer(text='Showing the top 3 results.')
            await msg.edit(embed=em)
        except KeyError:
            em = discord.Embed(color=discord.Color(value=0xf44e42), title="This is awkward, ain't it?")
            em.description = "Throughout the entire COC universe, there were no clans with your given name to be found..."
            await msg.edit(embed=em)

def setup(bot): 
    bot.add_cog(COC(bot)) 


						







