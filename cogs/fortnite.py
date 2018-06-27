import discord
import box
import json
from discord.ext import commands


class Fortnite:
    def __init__(self, bot):
        self.bot = bot
        with open("data/apikeys.json") as f:
            x = json.load(f)
        self.apikey = x['fnapi']

    @commands.command()
    async def fnsave(self, ctx, platform: str, *, username: str):
        """Save your Fortnite platform+name to the bot."""
        platform = platform.lower()
        if not platform in ("xbl", "psn", "pc"):
            return await ctx.send("Invalid platform!\n\n++**Platforms**__\n-`xbl` (Xbox Live)\n`psn` (Playstation)\n`PC` (Computer)")
        res = await self.bot.session.get(f"https://api.fortnitetracker.com/v1/profile/{platform.lower()}/{username}", headers={"TRN-Api-Key": self.apikey})
        data = await res.json()
        if data.get("error", "") == "Player Not Found":
            return await ctx.send("Oops, could not find that player. Command usage: *fnprofile [platform: xbl/psn/pc] [name: in-game name].")
        to_save = {
            "platform": platform,
            "username": username
        }
        await self.bot.db.fortnite.update_one({"id": ctx.author.id}, {"$set": to_save}, upsert=True)
        await ctx.send()

    @commands.command(aliases=["fn", "fnprofile", "fucknite"])
    async def fortnite(self, ctx, platform: str, *, username: str):
        """Gets your fortnite stats"""
        if not platform and not username:
            stuff = await self.bot.db.fortnite.find_one({"id": ctx.author.id})
            if not stuff:
                return await ctx.send("You didn't save your Fortnite stats to the bot yet! Use `*fnsave [platform] [username]` to do that.")
            platform = stuff['platform']
            username = stuff['username']
        if not platform.lower() in ("xbl", "psn", "pc"):
            return await ctx.send("Invalid platform!\n\n++**Platforms**__\n-`xbl` (Xbox Live)\n`psn` (Playstation)\n`PC` (Computer)")
        async with ctx.typing():
            try:
                res = await self.bot.session.get(f"https://api.fortnitetracker.com/v1/profile/{platform.lower()}/{username}", headers={"TRN-Api-Key": self.apikey})
                data = await res.json()
                if data.get("error", "") == "Player Not Found":
                    return await ctx.send("Oops, could not find that player. Command usage: *fnprofile [platform: xbl/psn/pc] [name: in-game name].")
                resp = box.Box(data)
                em = discord.Embed(color=ctx.author.color)
                em.title = resp.epicUserHandle
                em.description = f"{resp.epicUserHandle} on {resp.platformNameLong}"
                em.set_author(name=str(ctx.author), icon_url=ctx.author.avatar_url)
                em.set_thumbnail(url="https://cdn.discordapp.com/attachments/460894620545449986/461579014394609665/IMG_20180627_200804.png")
                try:
                    em.add_field(name="Solo", value=f"**Wins:** {resp.stats.p2.top1.value}\n**Top 25:** {resp.stats.p2.top25.displayValue}\n**Top 10:** {resp.stats.p2.top10.displayValue}\n**KD:** {resp.stats.p2.kd.displayValue}\n**Win Ratio:** {resp.stats.p2.winRatio.displayValue}%\n**Kills:** {resp.stats.p2.kills.displayValue}\n**Matches Played:** {resp.stats.p2.matches.displayValue}\n**Kills Per Match:** {resp.stats.p2.kpg.displayValue}")
                except box.BoxKeyError:
                    em.add_field(name="Solo", value="No Solos were played yet! :cry:")
                try:
                    em.add_field(name="Duos", value=f"**Wins:** {resp.stats.p10.top1.value}\n**Top 5:** {resp.stats.p10.top5.displayValue}\n**Top 12:** {resp.stats.p10.top12.displayValue}\n**KD:** {resp.stats.p10.kd.displayValue}\n**Win Ratio:** {resp.stats.p10.winRatio.displayValue}%\n**Kills:** {resp.stats.p10.kills.displayValue}\n**Matches Played:** {resp.stats.p10.matches.displayValue}\n**Kills Per Match:** {resp.stats.p10.kpg.displayValue}")
                except box.BoxKeyError:
                    em.add_field(name="Duos", value="No Duos were played yet! :cry:")
                try:
                    em.add_field(name="Squads", value=f"**Wins:** {resp.stats.p9.top1.value}\n**Top 3:** {resp.stats.p9.top3.displayValue}\n**Top 6:** {resp.stats.p9.top6.displayValue}\n**KD:** {resp.stats.p9.kd.displayValue}\n**Win Ratio:** {resp.stats.p9.winRatio.displayValue}%\n**Kills:** {resp.stats.p9.kills.displayValue}\n**Matches Played:** {resp.stats.p9.matches.displayValue}\n**Kills Per Match:** {resp.stats.p9.kpg.displayValue}")
                except box.BoxKeyError:
                    em.add_field(name="Squads", value="No Squads were played yet! :cry:")
                try:
                    em.add_field(name="Life Time Stats", value=f"**Score**: {resp.lifeTimeStats[6].value}\n**Matches Played:** {resp.lifeTimeStats[7].value}\n**Wins:** {resp.lifeTimeStats[8].value}\n**Win Ratio:** {resp.lifeTimeStats[9].value}\n**Kills:** {resp.lifeTimeStats[10].value}\n**KD:** {resp.lifeTimeStats[11].value}")
                except box.BoxKeyError:
                    em.add_field(name="Life Time Stats", value="**Failed to get life time stats.**")
                await ctx.send(embed=em)
            except Exception as e:
                await ctx.send("Something went wrong, please try again later.")
                

def setup(bot):
    bot.add_cog(Fortnite(bot))