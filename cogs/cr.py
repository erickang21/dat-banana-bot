import discord
import sys
import os
import io
import json
import ezjson
import clashroyale
import traceback
from discord.ext import commands


class CR:
    def __init__(self, bot):
        self.bot = bot
        with open('data/apikeys.json') as f:
            lol = json.load(f)
            self.token = lol['crapi']
        self.client = clashroyale.Client(token=self.token, is_async=True)
        self.cards = ['Ice Wizard', 'Hunter', 'Dart Goblin', 'Balloon', 'Skeleton Army', 'Royal Giant', 'Battle Ram', 'Minions', 'Bandit', 'Arrows', 'Mega Knight', 'Baby Dragon', 'Heal', 'Witch', 'Archers', 'Barbarians', 'Wizard', 'Rage', 'Guards', 'Giant Skeleton', 'Skeletons', 'Inferno Tower', 'Spear Goblins', 'Furnace', 'Cannon Cart', 'P.E.K.K.A', 'Bomber', 'Sparky', 'Ice Golem', 'Graveyard', 'Clone', 'Poison', 'Lightning', 'Cannon', 'Knight', 'Royal Ghost', 'Tesla', 'Dark Prince', 'Bomb Tower', 'Skeleton Barrel', 'Prince', 'Electro Wizard', 'Mega Minion',
                      'Musketeer', 'Giant', 'Mirror', 'Bowler', 'Mortar', 'Lava Hound', 'Rocket', 'Tornado', 'Night Witch', 'Goblin Hut', 'Fire Spirits', 'Tombstone', 'Princess', 'Barbarian Hut', 'Goblins', 'Valkyrie', 'The Log', 'Freeze', 'Inferno Dragon', 'Goblin Barrel', 'Lumberjack', 'Three Musketeers', 'Miner', 'X-Bow', 'Ice Spirit', 'Flying Machine', 'Executioner', 'Zappies', 'Elixir Collector', 'Golem', 'Magic Archer', 'Barbarian Barrel', 'Rascals', 'Mini P.E.K.K.A', 'Hog Rider', 'Minion Horde', 'Fireball', 'Goblin Gang', 'Elite Barbarians', 'Bats', 'Zap']

    def check_tag(self, crtag):
        for char in crtag:
            if char.upper() not in '0289PYLQGRJCUV':
                return False 
            return True
    
    def show_cards(self, cards):
        if len(cards) > 10:
            more_left = len(cards) - 10
            return "{}\n... and {} more.".format(" ".join([self.emoji(x) for x in cards]), more_left)
        else:
            return " ".join([self.emoji(x) for x in cards])

    def emoji(self, name):
        with open('data/emojis.json') as f:
            lol = json.loads(f.read())
        try:
            e = lol[str(name)]
            emo = str(self.bot.get_emoji(int(e)))
            return emo
        except KeyError:
            default = self.bot.get_emoji(407318200737595392)
            return str(default)


    async def get_tag(self, id):
        x = await self.bot.db.crtags.find_one({"id": str(id)})
        return x['tag'] if x is not None else None
    

    @commands.command()
    async def crsave(self, ctx, crtag):
        """Saves your CR tag to your account. Usage: *crsave [player tag]"""
        await ctx.trigger_typing()
        if not self.check_tag(crtag):
            return await ctx.send("That must be an invalid tag. Please use a valid tag. :x:")   
        await self.bot.db.crtags.update_one({"id": str(ctx.author.id)}, {"$set": {"tag": crtag}}, upsert=True)
        await ctx.send("Success. :white_check_mark: Your tag is now saved to your account.")


    @commands.command()
    async def crprofile(self, ctx, crtag=None):
        """Gets those sweet Stats for CR...Usage: *crprofile [tag]"""
        await ctx.trigger_typing()
        try:
            if crtag is None:
                    # with open('data/crtags.json') as f:
                    #     lol = json.load(f)
                    #     userid = str(ctx.author.id)
                    #     crtag = lol[userid]
                crtag = await self.get_tag(ctx.author.id)
                if not crtag:
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
            em.description = "Guess who else has CR stats? Our partner bot, [Statsy](https://bot.discord.io/statsy)"
            em.add_field(name='Trophies', value=f"{profile.trophies} {self.emoji('trophy')}")
            em.add_field(name='Personal Best', value=f"{profile.stats.maxTrophies} {self.emoji('trophy')}")
            em.add_field(name='XP Level', value=f"{profile.stats.level} {self.emoji('xplevel')}")
            em.add_field(name='Arena', value=f'{profile.arena.name}')
            em.add_field(name='Total Games', value=f"{profile.games.total} {self.emoji('battle')}")
            em.add_field(name='Wins', value=f"{profile.games.wins} ({profile.games.winsPercent * 100}% of all games) {self.emoji('battle')}")
            em.add_field(name='Three Crown Wins', value=f"{profile.stats.threeCrownWins} {self.emoji('threecrown')}")
            em.add_field(name='Losses', value=f"{profile.games.losses} ({profile.games.lossesPercent * 100}% of all games) {self.emoji('battle')}")
            em.add_field(name='Draws', value=f"{profile.games.draws} ({profile.games.drawsPercent * 100}% of all games) {self.emoji('battle')}")
            em.add_field(name='Win Rate', value=f"{(profile.games.wins / (profile.games.wins + profile.games.losses) * 100):.3f}% {self.emoji('sword')}")
            em.add_field(name='Favorite Card', value=f'{profile.stats.favoriteCard.name} {self.emoji(profile.stats.favoriteCard.name)}')
            if not profile.rank:
                globalrank = 'Unranked'
            else:
                globalrank = profile.rank
            em.add_field(name='Global Rank', value=f"{globalrank}{self.emoji('legendtrophy')}")    
            em.add_field(name='Challenge Max Wins', value=f"{profile.stats.challengeMaxWins} {self.emoji('12wins')}")
            em.add_field(name='Challenge Cards Won', value=f"{profile.stats.challengeCardsWon} {self.emoji('deck')}")
            em.add_field(name='Tourney Cards Won', value=f"{profile.stats.tournamentCardsWon} {self.emoji('deck')}") 
            try:                                                                                                                                               
                clan = await profile.get_clan()
                em.add_field(name='Clan', value=f"{clan.name} (#{clan.tag}) {self.emoji('clan')}", inline=False)
                clanroles = {
                    "member": "Member",
                    "elder": "Elder",
                    "coLeader": "Co-Leader",
                    "leader": "Leader"
                }
                em.add_field(name='Role', value=f'{clanroles[profile.clan.role]}', inline=False)                                                                                                                                                                      
                em.add_field(name='Clan Score', value=f"{clan.score} {self.emoji('trophy')}")
                em.add_field(name='Members', value=f'{len(clan.members)}/50')
                em.add_field(name='Donations', value=profile.clan.donations)
                em.add_field(name='Donations Received', value=profile.clan.donationsReceived)
                em.set_thumbnail(url=f'https://cr-api.github.io/cr-api-assets/arenas/arena{profile.arena.arenaID}.png') # This allows thumbnail to match your arena! Maybe it IS possible after all...
                em.set_footer(text='cr-api.com', icon_url='http://cr-api.com/static/img/branding/cr-api-logo.png')
            except AttributeError:
                em.add_field(name="Clan", value=f"No Clan {self.emoji('noclan')}", inline=False)
            await ctx.send(embed=em)
        except Exception as e:
            print(traceback.format_exc())




    @commands.command()
    async def crclan(self, ctx, clantag=None):
        """Shows info for a clan. Usage: *crclan [CLAN TAG]"""
        await ctx.trigger_typing()
        if clantag is None:
                # with open('data/crtags.json') as f:
                #     lol = json.load(f)
                #     userid = str(ctx.author.id)
                #     crtag = lol[userid]
            crtag = await self.get_tag(ctx.author.id)
            if not crtag:
                return await ctx.send("Uh-oh, no tag found! Use *crsave [tag] to save your tag to your Discord account. :x:")
        try:
            profile = await self.client.get_player(crtag)
            clan = await profile.get_clan()
        except AttributeError:
            em = discord.Embed(color=discord.Color(value=0xf44e42), title="Oof!")
            em.description = "You currently aren't in a clan."
            return await ctx.send(embed=em)
        except (clashroyale.errors.NotResponding, clashroyale.errors.ServerError) as e:
            print(e)
            color = discord.Color(value=0xf44e42)
            em = discord.Embed(color=color, title='Royale API error.')
            em.description = f"{e.code}: {e.error}"
            return await ctx.send(embed=em)
        color = discord.Color(value=0xf1f442)
        em = discord.Embed(color=color, title=f'{clan.name} ({clan.tag})')
        em.description = f'{clan.description}'
        em.add_field(name='Clan Trophies', value=f'{clan.score}')
        em.add_field(name='Members', value=f'{clan.memberCount}/50')
        em.add_field(name='Type', value=f'{clan.type}')
        em.add_field(name='Weekly Donations', value=f'{clan.donations}')
        em.add_field(name='Location', value=f'{clan.location.name}')
        # if clan.clan_chest.status == 'inactive':
        #     tier = "Inactive"
        # else:
        #     crowns = 0
        #     for m in clan.members:
        #         crowns += m.clan_chest_crowns
        #     if crowns < 70:
        #         tier = "0/10"
        #     if crowns > 70 and crowns < 160:
        #         tier = "1/10"
        #     if crowns > 160 and crowns < 270:
        #         tier = "2/10"
        #     if crowns > 270 and crowns < 400:
        #         tier = "3/10"
        #     if crowns > 400 and crowns < 550:
        #         tier = "4/10"
        #     if crowns > 550 and crowns < 720:
        #         tier = "5/10"
        #     if crowns > 720 and crowns < 910:
        #         tier = "6/10"
        #     if crowns > 910 and crowns < 1120:
        #         tier = "7/10"                        
        #     if crowns > 1120 and crowns < 1350:
        #         tier = "8/10"
        #     if crowns > 1350 and crowns < 1600:
        #         tier = "9/10"
        #     if crowns == 1600:
        #         tier = "10/10"
        #     em.add_field(name='Clan Chest Tier', value=f'{tier}')
        if not clan.war:
            war = "Not in Progress"
        else:
            if clan.war.state == "warDay":
                war = "War Day :crossed_swords:"
            elif clan.war.state == "collectionDay":
                war = f"Collection Day {self.emoji('deck')}"
        em.add_field(name="Clan War Status", value=war)
        em.add_field(name='Trophy Requirement', value=f'{clan.requiredScore}')
        em.set_thumbnail(url=f'{clan.badge.image}')
        em.set_footer(text='royaleapi.com', icon_url='http://cr-api.com/static/img/branding/cr-api-logo.png')
        await ctx.send(embed=em)




    @commands.command()
    async def crdeck(self, ctx, crtag=None):
        """What's that deck you got there? Find out!"""
        await ctx.trigger_typing()
        if crtag is None:
                # with open('data/crtags.json') as f:
                #     lol = json.load(f)
                # userid = str(ctx.author.id)
                # crtag = lol[userid]
            crtag = await self.get_tag(ctx.author.id)
            if not crtag:
                return await ctx.send("Uh-oh, no tag found! Use *cocsave [tag] to save your tag to your Discord account. :x:")
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
            getemoji = self.emoji(cardname) 
            e = getemoji if getemoji is not None else self.emoji('soon')
            deck += f"{getemoji} {cardname} - Level {card.level} \n"
            avgelixir += card.elixir
        avgelixir = f'{(avgelixir / 8):.1f}' 
        color = discord.Color(value=0x00ff00)
        em = discord.Embed(color=color, title=f'{profile.name} (#{profile.tag})')
        em.description = deck
        em.add_field(name='Average Elixir Cost', value=avgelixir)
        em.set_author(name='Battle Deck')
        em.set_footer(text='cr-api.com')
        await ctx.send(embed=em)


    @commands.command()
    async def crchests(self, ctx, crtag=None):
        """Get your upcoming chests!"""
        await ctx.trigger_typing()
        if crtag is None:
                # with open('data/crtags.json') as f:
                #     lol = json.load(f)
                # userid = str(ctx.author.id)
                # crtag = lol[userid]
            crtag = await self.get_tag(ctx.author.id)
            if not crtag:
                return await ctx.send("Uh-oh, no tag found! Use *cocsave [tag] to save your tag to your Discord account. :x:")
        try:
            profile = await self.client.get_player(crtag)
            chests = await self.client.get_player_chests(crtag)
        except (clashroyale.errors.NotResponding, clashroyale.errors.ServerError) as e:
            print(e)
            color = discord.Color(value=0xf44e42)
            em = discord.Embed(color=color, title='Royale API error.')
            em.description = f"{e.code}: {e.error}"
            return await ctx.send(embed=em)
        em = discord.Embed(color=discord.Color(value=0x00ff00), title='Player Chests')
        em.set_author(name=profile.name, icon_url=ctx.author.avatar_url)
        desc = ""
        for x in chests.upcoming:
            desc += f"{self.emoji(x)} "
        desc += "\n\n**Upcoming Chests**"
        em.description = desc
        em.add_field(name=self.emoji('super magical'), value=chests.superMagical, inline=False)
        em.add_field(name=self.emoji('magical'), value=chests.magical, inline=False)
        em.add_field(name=self.emoji('legendary'), value=chests.legendary, inline=False)
        em.add_field(name=self.emoji('epic'), value=chests.epic, inline=False)
        em.add_field(name=self.emoji('giant'), value=chests.giant, inline=False)
        em.set_footer(text="Royale API")
        await ctx.send(embed=em)


    @commands.command()
    async def crcards(self, ctx, crtag=None):
        await ctx.trigger_typing()
        if crtag is None:
                # with open('data/crtags.json') as f:
                #     lol = json.load(f)
                # userid = str(ctx.author.id)
                # crtag = lol[userid]
            crtag = await self.get_tag(ctx.author.id)
            if not crtag:
                return await ctx.send("Uh-oh, no tag found! Use *cocsave [tag] to save your tag to your Discord account. :x:")
        try:
            profile = await self.client.get_player(crtag)
        except (clashroyale.errors.NotResponding, clashroyale.errors.ServerError) as e:
            print(e)
            color = discord.Color(value=0xf44e42)
            em = discord.Embed(color=color, title='Royale API error.')
            em.description = f"{e.code}: {e.error}"
            return await ctx.send(embed=em)
        try:
            # all_cards = [x for x in self.cards]
            # all_pfp_cards = [x for x in profile.cards]
            # common = [x.name for x in all_pfp_cards if x.rarity == "Common"]
            # rare = [x.name for x in all_pfp_cards if x.rarity == "Rare"]
            # epic = [x.name for x in all_pfp_cards if x.rarity == "Epic"]
            # legendary = [x.name for x in all_pfp_cards if x.rarity == "Legendary"]
            # not_found = [x for x in all_cards if not x in all_pfp_cards] or f"All found! {str(discord.utils.get(self.bot.emojis, name='blobwave'))}"
            em = discord.Embed(color=discord.Color(value=0x00ff00), title=f"{profile.name} (#{profile.tag})")
            em.description = f"**Cards found:** {len(profile.cards)}/84"
            # em.add_field(name="Found Cards", value="-", inline=False)
            # em.add_field(name="Common", value=self.show_cards(common), inline=False)
            # em.add_field(name="Rare", value=self.show_cards(rare), inline=False)
            # em.add_field(name="Epic", value=self.show_cards(epic), inline=False)
            # em.add_field(name="Legendary", value=self.show_cards(legendary), inline=False)
            # em.add_field(name="Not Found", value=self.show_cards(not_found), inline=False)
            all_cards = [x for x in self.cards]
            all_profile_cards = [x for x in profile.cards]
            all_profile_cards_name = [x.name for x in profile.cards]
            found_common_cards = [x.name for x in all_profile_cards if x.rarity == "Common"]
            print(f"DEBUG: Common cards - {', '.join(found_common_cards)}")
            found_common_cards = list(map(lambda x: self.emoji(str(x)), found_common_cards))
            found_rare_cards = [x.name for x in all_profile_cards if x.rarity == "Rare"]
            print(f"DEBUG: Rare cards - {', ' .join(found_rare_cards)}")
            found_rare_cards = list(map(lambda x: self.emoji(str(x)), found_rare_cards))
            found_epic_cards = [x.name for x in all_profile_cards if x.rarity == "Epic"]
            print(f"DEBUG: epic cards - {', '.join(found_epic_cards)}")
            found_epic_cards = list(map(lambda x: self.emoji(str(x)), found_epic_cards))
            found_legendary_cards = [x.name for x in all_profile_cards if x.rarity == "Legendary"]
            print(f"DEBUG: legendary cards - {', '.join(found_legendary_cards)}")
            found_legendary_cards = list(map(lambda x: self.emoji(str(x)), found_legendary_cards))
            not_found_cards = [x for x in all_cards if x not in all_profile_cards_name]
            not_found_cards = " ".join(list(map(lambda x: self.emoji(x), not_found_cards))) or f"All cards found! :tada:"
            print(f"DEBUG: Not found cards - {', '.join(not_found_cards)}")
            #print(" ".join([self.emoji(x) for x in not_found_cards])
            #print(" ".join([self.emoji(x) for x in found_legendary_cards]))
            em.add_field(name="Common", value=" ".join(found_common_cards), inline=False)  
            em.add_field(name="Rare", value=" ".join(found_rare_cards), inline=False) 
            em.add_field(name="Epic", value=" ".join(found_epic_cards), inline=False) 
            em.add_field(name="Legendary", value=" ".join(found_legendary_cards), inline=False) 
            em.add_field(name="Not Found", value=not_found_cards, inline=False) 
            await ctx.send(embed=em)
        except Exception as e:
            traceback_text = "\n".join(traceback.format_exception(type(e), e, e.__traceback__, 10))
            return await ctx.send(f"An unknown error occurred:\n```{traceback_text}```")

def setup(bot): 
    bot.add_cog(CR(bot)) 
