import discord
import sys
import os
import io
import json
import ezjson
import clashroyale
from discord.ext import commands


class CR:
    def __init__(self, bot):
        self.bot = bot
        with open('data/apikeys.json') as f:
            lol = json.load(f)
            self.token = lol.get("crapi")
        self.client = clashroyale.Client(token=self.token, is_async=True)


    def check_tag(self, crtag):
        for char in crtag:
            if char.upper() not in '0289PYLQGRJCUV':
                return False 
            return True      


    def get_emoji(self, emoji):
        with open('data/emojis.json') as f:
            lol = json.load(f)
            e = lol[emoji]
            return self.bot.get_emoji(e)


    

    @commands.command()
    async def crsave(self, ctx, crtag=None):
        """Saves your CR tag to your account. Usage: *crsave [player tag]"""
        if crtag is None:
            return await ctx.send("Please enter a tag to save. Usage: *crsave [tag]")
        if not self.check_tag(crtag):
            return await ctx.send("That must be an invalid tag. Please use a valid tag. :x:")   
        ezjson.dump("data/crtags.json", ctx.author.id, crtag)                
        await ctx.send("Success. :white_check_mark: Your tag is now saved to your account.")


    @commands.command()
    async def crprofile(self, ctx, crtag=None):
        """Gets those sweet Stats for CR...Usage: *crprofile [tag]"""
        if crtag is None:
            try:
                with open('data/crtags.json') as f:
                    lol = json.load(f)
                    userid = str(ctx.author.id)
                    crtag = lol[userid]
            except KeyError:
                return await ctx.send("Uh-oh, no tag found! Use `*crsave [tag]` to save your tag to your Discord account. :x:")
            try:
                profile = await self.client.get_player(crtag)
            except (clashroyale.errors.NotResponding, clashroyale.errors.ServerError) as e:
                print(e)
                color = discord.Color(value=0xf44e42)
                em = discord.Embed(color=color, title='Royale API error.')
                em.description = f"{e.code}: {e.error}"
                return await ctx.send(embed=em)
            color = discord.Color(value=0xf1f442)
            em = discord.Embed(color=color, title=f'{profile.name} (#{profile.tag})')
            em.add_field(name='Trophies', value=f'{profile.trophies}')
            em.add_field(name='Personal Best', value=f'{profile.stats.max_trophies}')
            em.add_field(name='XP Level', value=f'{profile.stats.level}')
            em.add_field(name='Arena', value=f'{profile.arena.name}')
            em.add_field(name='Wins', value=profile.games.wins)
            em.add_field(name='Losses', value=profile.games.losses)
            em.add_field(name='Draws', value=profile.games.draws)
            em.add_field(name='Win Rate', value=f'{(profile.games.wins / (profile.games.wins + profile.games.losses) * 100):.3f}%')
            em.add_field(name='Favorite Card', value=f'{profile.stats.favorite_card.name}')                                                                                                                                                 
            em.set_author(name=f'dat banana bot Stats')
            em.set_thumbnail(url=f'https://cr-api.github.io/cr-api-assets/arenas/arena{profile.arena.arenaID}.png') # This allows thumbnail to match your arena! Maybe it IS possible after all...
            await ctx.send(embed=em)
            try:
                clan = await profile.get_clan()
            except:
                pass
            if profile.clan.role:
                color = discord.Color(value=0xf1f442)
                em = discord.Embed(color=color, title='Clan')
                em.description = f'{clan.name} (#{clan.tag})'
                em.add_field(name='Role', value=f'{profile.clan.role}')                                                                                                                                                                      
                em.add_field(name='Clan Score', value=f'{clan.score}')
                em.add_field(name='Members', value=f'{len(clan.members)}/50')
                em.set_thumbnail(url=clan.badge.image)
                await ctx.send(embed=em)
            else:
                color = discord.Color(value=0xf1f442)
                em = discord.Embed(color=color, title='Clan')
                em.description = 'No Clan'
                em.set_thumbnail(url='http://i1253.photobucket.com/albums/hh599/bananaboy21/maxresdefault_zpseuid4jln.jpg') # This is the url for the No Clan symbol.   
                await ctx.send(embed=em)
            profile = await self.client.get_player(crtag)
            color = discord.Color(value=0xf1f442)
            em = discord.Embed(color=color)
            em.add_field(name='Challenge Max Wins', value=f'{profile.stats.challenge_max_wins}')
            em.add_field(name='Challenge Cards Won', value=f'{profile.stats.challenge_cards_won}')
            em.add_field(name='Tourney Cards Won', value=f'{profile.stats.tournament_cards_won}')
            em.set_author(name='Challenge/Tourney Stats')
            em.set_thumbnail(url='http://vignette4.wikia.nocookie.net/clashroyale/images/a/a7/TournamentIcon.png/revision/latest?cb=20160704151823')
            em.set_footer(text='cr-api.com', icon_url='http://cr-api.com/static/img/branding/cr-api-logo.png')
            await ctx.send(embed=em)
        else:
            profile = await self.client.get_player(crtag)
            color = discord.Color(value=0xf1f442)
            em = discord.Embed(color=color, title=f'{profile.name} (#{profile.tag})')
            em.add_field(name='Trophies', value=f'{profile.trophies}')
            em.add_field(name='Personal Best', value=f'{profile.stats.max_trophies}')
            em.add_field(name='XP Level', value=f'{profile.stats.level}')
            em.add_field(name='Arena', value=f'{profile.arena.name}')
            em.add_field(name='Wins/Losses/Draws', value=f'{profile.games.wins}/{profile.games.draws}/{profile.games.losses}')
            em.add_field(name='Win Rate', value=f'{(profile.games.wins / (profile.games.wins + profile.games.losses) * 100):.3f}%')
            em.add_field(name='Favorite Card', value=f'{profile.stats.favorite_card.name}')                                                                                                                                                 
            em.set_author(name=f'dat banana bot Stats')
            em.set_thumbnail(url=f'https://cr-api.github.io/cr-api-assets/arenas/arena{profile.arena.arenaID}.png') # This allows thumbnail to match your arena! Maybe it IS possible after all...
            await ctx.send(embed=em)
            try:
                clan = await profile.get_clan()
            except:
                pass
            if profile.clan.role:
                color = discord.Color(value=0xf1f442)
                em = discord.Embed(color=color, title='Clan')
                em.description = f'{clan.name} (#{clan.tag})'
                em.add_field(name='Role', value=f'{profile.clan.role}')                                                                                                                                                                      
                em.add_field(name='Clan Score', value=f'{clan.score}')
                em.add_field(name='Members', value=f'{len(clan.members)}/50')
                em.set_thumbnail(url=clan.badge.image)
                await ctx.send(embed=em)
            else:
                color = discord.Color(value=0xf1f442)
                em = discord.Embed(color=color, title='Clan')
                em.description = 'No Clan'
                em.set_thumbnail(url='http://i1253.photobucket.com/albums/hh599/bananaboy21/maxresdefault_zpseuid4jln.jpg') # This is the url for the No Clan symbol.   
                await ctx.send(embed=em)
            profile = await self.client.get_player(crtag)
            color = discord.Color(value=0xf1f442)
            em = discord.Embed(color=color)
            em.add_field(name='Challenge Max Wins', value=f'{profile.stats.challenge_max_wins}')
            em.add_field(name='Challenge Cards Won', value=f'{profile.stats.challenge_cards_won}')
            em.add_field(name='Tourney Cards Won', value=f'{profile.stats.tournament_cards_won}')
            em.set_author(name='Challenge/Tourney Stats')
            em.set_thumbnail(url='http://vignette4.wikia.nocookie.net/clashroyale/images/a/a7/TournamentIcon.png/revision/latest?cb=20160704151823')
            em.set_footer(text='cr-api.com', icon_url='http://cr-api.com/static/img/branding/cr-api-logo.png')
            await ctx.send(embed=em)


    @commands.command()
    async def crclan(self, ctx, clantag=None):
        """Shows info for a clan. Usage: *crclan [CLAN TAG]"""
        if clantag is None:
            try:
                with open('data/crtags.json') as f:
                    lol = json.load(f)
                    userid = str(ctx.author.id)
                    crtag = lol[userid]
            except KeyError:
                return await ctx.send("Uh-oh, no tag found! Use *crsave [tag] to save your tag to your Discord account. :x:")
            else:
                try:
                    profile = await self.client.get_player(crtag)
                    clan = await profile.get_clan()
                except (clashroyale.errors.NotResponding, clashroyale.errors.ServerError) as e:
                    print(e)
                    color = discord.Color(value=0xf44e42)
                    em = discord.Embed(color=color, title='Royale API error.')
                    em.description = f"{e.code}: {e.error}"
                    return await ctx.send(embed=em)
                color = discord.Color(value=0xf1f442)
                em = discord.Embed(color=color, title=f'{clan.name}')
                em.description = f'{clan.description}'
                em.add_field(name='Clan Trophies', value=f'{clan.score}')
                em.add_field(name='Members', value=f'{clan.memberCount}/50')
                em.add_field(name='Type', value=f'{clan.type}')
                em.add_field(name='Weekly Donations', value=f'{clan.donations}')
                em.add_field(name='Location', value=f'{clan.location.name}')
                if clan.clan_chest.status == 'inactive':
                    tier = "Inactive"
                else:
                    crowns = 0
                    for m in clan.members:
                        crowns += m.clan_chest_crowns
                    if crowns < 70:
                        tier = "0/10"
                    if crowns > 70 and crowns < 160:
                        tier = "1/10"
                    if crowns > 160 and crowns < 270:
                        tier = "2/10"
                    if crowns > 270 and crowns < 400:
                        tier = "3/10"
                    if crowns > 400 and crowns < 550:
                        tier = "4/10"
                    if crowns > 550 and crowns < 720:
                        tier = "5/10"
                    if crowns > 720 and crowns < 910:
                        tier = "6/10"
                    if crowns > 910 and crowns < 1120:
                        tier = "7/10"                        
                    if crowns > 1120 and crowns < 1350:
                        tier = "8/10"
                    if crowns > 1350 and crowns < 1600:
                        tier = "9/10"
                    if crowns == 1600:
                        tier = "10/10"
                    em.add_field(name='Clan Chest Tier', value=f'{tier}')
                    em.add_field(name='Trophy Requirement', value=f'{clan.requiredScore}')
                    em.set_author(name=f'#{clan.tag}')
                    em.set_thumbnail(url=f'{clan.badge.image}')
                    em.set_footer(text='cr-api.com', icon_url='http://cr-api.com/static/img/branding/cr-api-logo.png')
                    await ctx.send(embed=em)
        else:
            clan = await self.client.get_clan(clantag)
            color = discord.Color(value=0xf1f442)
            em = discord.Embed(color=color, title=f'{clan.name}')
            em.description = f'{clan.description}'
            em.add_field(name='Clan Trophies', value=f'{clan.score}')
            em.add_field(name='Members', value=f'{clan.memberCount}/50')
            em.add_field(name='Type', value=f'{clan.type}')
            em.add_field(name='Weekly Donations', value=f'{clan.donations}')
            em.add_field(name='Location', value=f'{clan.location.name}')
            if clan.clan_chest.status == 'inactive':
                tier = "Inactive"
            else:
                crowns = 0
                for m in clan.members:
                    crowns += m.clan_chest_crowns
                if crowns < 70:
                    tier = "0/10"
                if crowns > 70 and crowns < 160:
                    tier = "1/10"
                if crowns > 160 and crowns < 270:
                    tier = "2/10"
                if crowns > 270 and crowns < 400:
                    tier = "3/10"
                if crowns > 400 and crowns < 550:
                    tier = "4/10"
                if crowns > 550 and crowns < 720:
                    tier = "5/10"
                if crowns > 720 and crowns < 910:
                    tier = "6/10"
                if crowns > 910 and crowns < 1120:
                    tier = "7/10"
                if crowns > 1120 and crowns < 1350:
                    tier = "8/10"
                if crowns > 1350 and crowns < 1600:
                    tier = "9/10"
                if crowns == 1600:
                    tier = "10/10"
            em.add_field(name='Clan Chest Tier', value=f'{tier}')
            em.add_field(name='Trophy Requirement', value=f'{clan.requiredScore}')
            em.set_author(name=f'#{clan.tag}')
            em.set_thumbnail(url=f'{clan.badge.image}')
            em.set_footer(text='cr-api.com', icon_url='http://cr-api.com/static/img/branding/cr-api-logo.png')
            await ctx.send(embed=em)


    @commands.command()
    async def crdeck(self, ctx, crtag=None):
        """What's that deck you got there? Find out!"""
        if crtag is None:
            try:
                with open('data/crtags.json') as f:
                    lol = json.load(f)
                    userid = str(ctx.author.id)
                    crtag = lol[userid]
            except KeyError:
                return await ctx.send("Uh-oh, no tag found! Use *cocsave [tag] to save your tag to your Discord account. :x:")
            else:
                try:
                    profile = await self.client.get_player(crtag)
                except (clashroyale.errors.NotResponding, clashroyale.errors.ServerError) as e:
                    print(e)
                    color = discord.Color(value=0xf44e42)
                    em = discord.Embed(color=color, title='Royale API error.')
                    em.description = f"{e.code}: {e.error}"
                    return await ctx.send(embed=em)
                deck = ''
                avgelixir = 0
                for card in profile.current_deck:
                    cardname = card.name 
                    getemoji = self.get_emoji(cardname)
                    if getemoji is None:
                        getemoji = self.bot.get_emoji("soon")
                    deck += f"{cardname} {getemoji} - Level {card.level} \n"
                    avgelixir += card.elixir
                avgelixir = f'{(avgelixir / 8):.1f}' 
                color = discord.Color(value=0x00ff00)
                em = discord.Embed(color=color, title=f'{profile.name} (#{profile.tag})')
                em.description = deck
                em.add_field(name='Average Elixir Cost', value=avgelixir)
                em.set_author(name='Battle Deck')
                em.set_footer(text='cr-api.com')
                await ctx.send(embed=em)
        else:
            profile = await self.client.get_player(crtag)
            deck = ''
            avgelixir = 0
            for card in profile.current_deck:
                deck += f"{card.name}{self.get_emoji(card.name)}{card.level} \n"
                avgelixir += card.elixir
            avgelixir = f'{(avgelixir / 8):.1f}' 
            color = discord.Color(value=0x00ff00)
            em = discord.Embed(color=color, title=f'{profile.name} (#{profile.tag})')
            em.description = deck
            em.add_field(name='Average Elixir Cost', value=avgelixir)
            em.set_author(name='Battle Deck')
            em.set_footer(text='cr-api.com')
            await ctx.send(embed=em)


        

def setup(bot): 
    bot.add_cog(CR(bot)) 
