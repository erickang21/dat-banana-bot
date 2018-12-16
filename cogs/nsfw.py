import discord
import aiohttp
import box
from discord.ext import commands
from .utils.utils import Utils

class NSFW:
    """
    I am in no way responsible for you breaking your eyes with commands under this class.

    All commands are CLEARLY labelled NSFW in the descrption of the respective commands.

    If you choose to use these commands, do so at your own risk.

    If you run out of eyewash because you saw too much here, then blame yourself and your 
    lack of self-control.
    """
    def __init__(self, bot):
        self.bot = bot
        self.utils = Utils(bot)

    async def req(self, url):
        res = await self.bot.session.get(f"https://nekos.life/api/v2/img/{url}")
        res = await res.json()
        return box.Box(res)

    async def handle_not_upvoted(self, ctx):
        em = discord.Embed(color=0xfc281d, title="It's No Nut November!")
        em.description = """
Hey! That means no nutting. Get some self control of yourself.

If you seriously can't, I'll do you a favor and run this command **after you upvote me on Discord Bot List.** 

It ain't hard, I got the link right here!

https://discordbots.org/bot/388476336777461770/vote

All you gotta do is hit that giant **VOTE** button!

(If you are seeing this message after upvoting, DBL's API is a bit slow, so you will have to wait around 5-10 minutes before retrying this command.)
"""
        await ctx.send(embed=em)

    # async def __local_check(self, ctx):
    #     if not ctx.channel.nsfw:
    #         await ctx.send("Are you trying to **kill innocent people's eyes**?? I think not!")
    #     return ctx.channel.nsfw

    @commands.command()
    async def feet(self, ctx, is_gif=None):
        """WARNING: NSFW command. Gets a random picture of feet."""
        if not ctx.channel.nsfw:
            return await ctx.send("Are you trying to **kill innocent people's eyes**?? I think not!")

        res = await self.req("feetg")
        em = discord.Embed(color=0xf9e236, title="Feet :eggplant:")
        em.set_image(url=res.url)
        em.set_footer(text=f"Requested by: {str(ctx.author)} | Powered by nekos.life", icon_url=ctx.author.avatar_url)
        await ctx.send(embed=em)


    @commands.command()
    async def hentai(self, ctx, is_gif=None):
        """WARNING: NSFW command. Gets a hentai picture."""
        if not ctx.channel.nsfw:
            return await ctx.send("Are you trying to **kill innocent people's eyes**?? I think not!")

        res = await self.req("Random_hentai_gif")
        em = discord.Embed(color=0xf9e236, title="Hentai :eggplant: ")
        em.set_image(url=res.url)
        em.set_footer(text=f"Requested by: {str(ctx.author)} | Powered by nekos.life", icon_url=ctx.author.avatar_url)
        await ctx.send(embed=em)


    @commands.command()
    async def boobs(self, ctx):
        """WARNING: NSFW command. Gets pictures of boobs."""
        if not ctx.channel.nsfw:
            return await ctx.send("Are you trying to **kill innocent people's eyes**?? I think not!")
        if not ctx.channel.nsfw:
            return await ctx.send("Are you trying to **kill innocent people's eyes**?? I think not!")

        res = await self.req("boobs")
        em = discord.Embed(color=0xf9e236, title="Boobs :eggplant: ")
        em.set_image(url=res.url)
        em.set_footer(text=f"Requested by: {str(ctx.author)} | Powered by nekos.life", icon_url=ctx.author.avatar_url)
        await ctx.send(embed=em)

    @commands.command()
    async def lewdneko(self, ctx):
        """WARNING: NSFW command. Gets a picture of a lewd neko."""
        if not ctx.channel.nsfw:
            return await ctx.send("Are you trying to **kill innocent people's eyes**?? I think not!")

        res = await self.req("nsfw_neko_gif")
        em = discord.Embed(color=0xf9e236, title="Lewd Neko :eggplant: ")
        em.set_image(url=res.url)
        em.set_footer(text=f"Requested by: {str(ctx.author)} | Powered by nekos.life", icon_url=ctx.author.avatar_url)
        await ctx.send(embed=em)

    @commands.command(aliases=['nsfwpfp'])
    async def nsfwavatar(self, ctx):
        """WARNING: NSFW command. Gets you a lewd profile picture."""
        if not ctx.channel.nsfw:
            return await ctx.send("Are you trying to **kill innocent people's eyes**?? I think not!")

        res = await self.req("nsfw_avatar")
        em = discord.Embed(color=0xf9e236, title="Lewd Profile Picture :eggplant: ")
        em.set_image(url=res.url)
        em.set_footer(text=f"Requested by: {str(ctx.author)} | Powered by nekos.life", icon_url=ctx.author.avatar_url)
        await ctx.send(embed=em)

    @commands.command()
    async def lesbian(self, ctx):
        """WARNING: NSFW command. Gets you a lesbian pic."""
        if not ctx.channel.nsfw:
            return await ctx.send("Are you trying to **kill innocent people's eyes**?? I think not!")

        res = await self.req("les")
        em = discord.Embed(color=0xf9e236, title="Lesbian :eggplant: ")
        em.set_image(url=res.url)
        em.set_footer(text=f"Requested by: {str(ctx.author)} | Powered by nekos.life", icon_url=ctx.author.avatar_url)
        await ctx.send(embed=em)


def setup(bot):
    bot.add_cog(NSFW(bot))
