import discord
import brawlstats
from discord.ext import commands


class BS(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.client = brawlstats.BrawlAPI(
            token=bot.config.bsapi,
            session=bot.session,
            is_async=True
        )

    def check_tag(self, tag):
        return [char for char in tag if char.upper() not in '0289PYLQGRJCUV']

    async def get_tag(self, id):
        find = await self.bot.db.bstags.find_one({"id": id})
        return find['tag']

    def emoji(self, _id):
        return self.bot.get_emoji(_id)

    def brawler(self, name):
        return discord.utils.get(self.bot.emojis, name=name)

    def cog_command_error(self, ctx, error):
        if isinstance(error, brawlstats.RequestError):
            em = discord.Embed(
                color=discord.Color.red(),
                title=f'{error.code} - {error.__class__.__name__}',
                description=error.error.split('\nURL')[0]  # chop off the requested URL
            )
            await ctx.send(embed=em)

    @commands.command()
    async def bssave(self, ctx, tag):
        """Saves your Brawl Stars tag to your Discord account."""
        tag = tag.strip("#")
        invalid_chars = self.check_tag(tag)
        if invalid_chars:
            return await ctx.send(f"Looks like that's an invalid tag!\nInvalid characters: {', '.join()}")
        await self.bot.db.bstags.update_one({"id": ctx.author.id}, {"$set": {"tag": tag}}, upsert=True)
        await ctx.send(f"Your Brawl Stars tag has been successfully saved. {self.emoji(484897652220362752)}")


    @commands.command()
    async def bsprofile(self, ctx, tag=None):
        await ctx.trigger_typing()
        if not tag:
            tag = await self.get_tag(ctx.author.id)
            if not tag:
                return await ctx.send("You didn't save a Brawl Stars tag to your profile. Time to get it saved!")
        else:
            tag = tag.strip('#')
            invalid_chars = self.check_tag(tag)
            if invalid_chars:
                return await ctx.send(f"Invalid characters: {', '.join(invalid_chars)}")

        profile = await self.client.get_player(tag)
        club = profile.club
        em = discord.Embed(color=0x00ff00, title=f"{profile.name} (#{profile.tag})")
        em.add_field(name="Trophies", value=f"{profile.trophies} {self.emoji(523919154630361088)}")
        em.add_field(name="Highest Trophies", value=f"{profile.highest_trophies} {self.emoji(523919154630361088)}")
        em.add_field(name="XP Level", value=f"{profile.expLevel} ({profile.exp_fmt}) {self.emoji(523924578314092544)}")
        em.add_field(name="Victories", value=f"**Total:** {profile.victories} {self.emoji(523919154751733762)}\n\
            **Solo Showdown:** {profile.solo_showdown_victories} {self.emoji(523923170755870720)}\n\
            **Duo Showdown:** {profile.duo_showdown_victories} {self.emoji(523923170671984656)}")
        em.add_field(name="Best Time as Big Brawler", value=f"{profile.best_time_as_big_brawler} {self.emoji(523923170970042378)}")
        em.add_field(name="Best Robo Rumble Time", value=f"{profile.best_robo_rumble_time} {self.emoji(523926186620092426)}")
        if club:
            em.add_field(name="Club", value=f"{club.name} (#{club.tag})", inline=False)
            em.add_field(name="Role", value=club.role)
            em.add_field(name="Trophies", value=club.trophies)
            em.add_field(name="Required Trophies", value=club.required_trophies)
            em.add_field(name="Members", value=club.members)
        else:
            em.add_field(name="Club", value=f"No club. {self.bot.get_emoji(522524669459431430)}")
        brawlers = ""
        for x in profile.brawlers:
            brawlers += f"{self.brawler(x.name.lower())} {x.power}"
        em.add_field(name="Brawlers", value=f"**{profile.brawlers_unlocked}/29**\n\n{brawlers}", inline=False)
        em.set_thumbnail(url=profile.avatar_url)
        await ctx.send(embed=em)

    @commands.command(aliases=["bsclan"])
    async def bsclub(self, ctx, tag=None):
        await ctx.trigger_typing()
        if not tag:
            profile_tag = await self.get_tag(ctx.author.id)
            if not profile_tag:
                return await ctx.send("You didn't save a Brawl Stars tag to your profile. Time to get it saved!")
            profile = await self.client.get_profile(profile_tag)
            club = await profile.get_club()
        else:
            tag = tag.strip('#')
            invalid_chars = self.check_tag(tag)
            if invalid_chars:
                return await ctx.send(f"Invalid characters: {', '.join(invalid_chars)}")
            club = await self.client.get_club(tag)

        em = discord.Embed(color=ctx.author.color, title=f"{club.name} (#{club.tag})")
        em.description = club.description
        em.add_field(name="Trophies", value=f"{club.trophies}")
        em.add_field(name="Members", value=f"**{club.members_count}**/100")
        em.add_field(name="Online Members", value=f"**{club.online_members}**/{club.members_count}")
        em.add_field(name="Required Trophies", value=club.required_trophies)
        em.add_field(name="Status", value=club.status)
        em.set_thumbnail(url=club.badge_url)
        await ctx.send(embed=em)




def setup(bot):
    bot.add_cog(BS(bot))