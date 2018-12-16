import discord
import brawlstats
from discord.ext import commands


class BS:
    def __init__(self, bot):
        self.bot = bot
        self.client = brawlstats.Client(bot.config.bsapi, is_async=True)

    def check_tag(self, tag):
        for char in tag:
            if char.upper() not in '0289PYLQGRJCUV':
                return False 
            return True
        
    async def get_tag(self, id):
        find = await self.bot.db.bstags.find_one({"id": id})
        return find['tag']
    
    def emoji(self, _id):
        return self.bot.get_emoji(_id)

    def brawler(self, name):
        return discord.utils.get(self.bot.emojis, name=name)

    @commands.command()
    async def bssave(self, ctx, tag):
        """Saves your Brawl Stars tag to your Discord account."""
        if not self.check_tag(tag):
            return await ctx.send("Looks like that's an invalid tag! Make it valid. :)")
        find = await self.bot.db.bstags.find_one({"id": ctx.author.id})
        if not tag.startswith("#"):
            tag = "#" + tag
        await self.bot.db.bstags.update_one({"id": ctx.author.id}, {"$set": {"tag": tag}}, upsert=True)
        await ctx.send(f"Your Brawl Stars tag has been successfully saved." + " (Your previously saved tag was deleted.)" if find else "")


    @commands.command()
    async def bsprofile(self, ctx, tag=None):
        if not tag:
            tag = await self.get_tag(ctx.author.id)
            if not tag:
                return await ctx.send("You didn't save a Brawl Stars tag to your profile. Time to get it saved!")
        profile = await self.client.get_profile(tag)
        club = profile.club
        em = discord.Embed(color=0x00ff00, title=f"{profile.name} (#{profile.tag})")
        em.add_field(name="Trophies", value=f"{profile.trophies} {self.emoji(523919154630361088)}")
        em.add_field(name="Highest Trophies", value=f"{profile.highestTrophies} {self.emoji(523919154630361088)}")
        em.add_field(name="XP Level", value=f"{profile.expLevel} ({profile.expFmt}) {self.emoji(523924578314092544)}")
        em.add_field(name="Victories", value=f"**Total:** {profile.victories} {self.emoji(523919154751733762)}\n**Solo Showdown:** {profile.soloShowdownVictories} {self.emoji(523923170755870720)}\n**Duo Showdown:** {profile.duoShowdownVictories} {self.emoji(523923170671984656)}")
        em.add_field(name="Best Time as Boss", value=f"{profile.best_time_as_boss} {self.emoji(523923170970042378)}")
        em.add_field(name="Best Robo Rumble Time", value=f"{profile.best_robo_rumble_time} {self.emoji(523926186620092426)}")
        if not club:
            em.add_field(name="Club", value=f"No club. {self.bot.get_emoji(522524669459431430)}")
        else:
            em.add_field(name="Club", value=f"{club.name} (#{club.tag})", inline=False)
            em.add_field(name="Role", value=club.role)
            em.add_field(name="Trophies", value=club.trophies)
            em.add_field(name="Required Trophies", value=club.required_trophies)
            em.add_field(name="Members", value=club.members)
        brawlers = ""
        for x in profile.brawlersUnlocked:
            brawlers += f"{self.brawler(x.name)} {x.level} "
        em.add_field(name="Brawlers", value=brawlers, inline=False)
        em.set_thumbnail(url=profile.avatarUrl)
        await ctx.send(embed=em)
    
def setup(bot):
    bot.add_cog(BS(bot))