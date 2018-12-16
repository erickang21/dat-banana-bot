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
        return find

    @commands.command()
    async def bssave(self, ctx, tag):
        """Saves your Brawl Stars tag to your Discord account."""
        if not self.check_tag(tag):
            return await ctx.send("Looks like that's an invalid tag! Make it valid. :)")
        find = await self.bot.db.bstags.find_one({"id": ctx.author.id})
        await self.bot.db.bstags.update_one({"id": ctx.author.id}, {"$set": {"tag": tag}}, upsert=True)
        await ctx.send(f"Your Brawl Stars tag has been successfully saved." + " (Your previously saved tag was deleted.)" if find else "")


    @commands.command()
    async def bsprofile(self, ctx, tag=None):
        if not tag:
            tag = await self.get_tag(ctx.author.id)
            if not tag:
                return await ctx.send("You didn't save a Brawl Stars tag to your profile. Time to get it saved!")
        profile = await self.client.get_profile(tag)
        em = discord.Embed(color=0x00ff00, title=f"{profile.name} (#{profile.tag})")
        em.add_field(name="Trophies", value=profile.trophies)
        em.add_field(name="Highest Trophies", value=profile.highestTrophies)
        em.add_field(name="XP Level", value=f"{profile.expLevel} ({profile.expFmt})")
        em.add_field(name="Brawlers Unlocked", value=profile.brawlersUnlocked)
        em.add_field(name="Victories", value=f"**Total:** {profile.victories}\n**Solo Showdown:** {profile.soloShowdownVictories}\n**Duo Showdown:** {profile.duoShowdownVictories}")
        em.set_thumbnail(url=profile.avatarUrl)
    
def setup(bot):
    bot.add_cog(BS(bot))