import discord
import aiohttp
from discord.ext import commands


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


    # async def __local_check(self, ctx):
    #     if not ctx.channel.nsfw:
    #         await ctx.send("Are you trying to **kill innocent people's eyes**?? I think not!")
    #     return ctx.channel.nsfw

    @commands.command()
    async def feet(self, ctx, is_gif=None):
        """WARNING: NSFW command. Gets a random picture of feet."""
        if not ctx.channel.nsfw:
            return await ctx.send("Are you trying to **kill innocent people's eyes**?? I think not!")
        if not is_gif:
            resp = await self.bot.session.get("https://nekos.life/api/v2/img/feet")
        else:
            resp = await self.bot.session.get("https://nekos.life/api/v2/img/feetg")
        resp = await resp.json()
        em = discord.Embed(color=0xf9e236, title="Here you go! Enjoy! :wink: :eggplant: ")
        em.set_author(name=f"Requested by {ctx.author.name}", icon_url=ctx.author.avatar_url)
        em.set_image(url=resp['url'])
        await ctx.send(embed=em)


    @commands.command()
    async def hentai(self, ctx, is_gif=None):
        """WARNING: NSFW command. Gets a hentai picture."""
        if not ctx.channel.nsfw:
            return await ctx.send("Are you trying to **kill innocent people's eyes**?? I think not!")
        if not is_gif:
            resp = await self.bot.session.get("https://nekos.life/api/v2/img/hentai")
        else:
            resp = await self.bot.session.get("https://nekos.life/api/v2/img/Random_hentai_gif")
        resp = await resp.json()
        em = discord.Embed(color=0xf9e236, title="Here you go! Enjoy! :wink: :eggplant: ")
        em.set_author(name=f"Requested by {ctx.author.name}", icon_url=ctx.author.avatar_url)
        em.set_image(url=resp['url'])
        await ctx.send(embed=em)


    @commands.command()
    async def boobs(self, ctx):
        """WARNING: NSFW command. Gets pictures of boobs."""
        if not ctx.channel.nsfw:
            return await ctx.send("Are you trying to **kill innocent people's eyes**?? I think not!")
        resp = await self.bot.session.get("https://nekos.life/api/v2/img/boobs")
        resp = await resp.json()
        em = discord.Embed(color=0xf9e236, title="Here you go! Enjoy! :wink: :eggplant: ")
        em.set_author(name=f"Requested by {ctx.author.name}", icon_url=ctx.author.avatar_url)
        em.set_image(url=resp['url'])
        await ctx.send(embed=em)


def setup(bot):
    bot.add_cog(NSFW(bot))
