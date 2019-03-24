import discord
from discord.ext import commands 
import box

class Anime(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    async def req(self, url):
        res = await self.bot.session.get(f"https://nekos.life/api/v2/img/{url}")
        res = await res.json()
        return box.Box(res)

    @commands.command()
    async def baka(self, ctx):
        """Random anime picture of BAKA."""
        await ctx.trigger_typing()
        res = await self.req("baka")
        em = discord.Embed(color=ctx.author.color, title="BAKA!")
        em.set_image(url=res.url)
        em.set_footer(text=f"Requested by: {str(ctx.author)} | Powered by nekos.life", icon_url=ctx.author.avatar_url)
        await ctx.send(embed=em)

    
    @commands.command()
    async def cuddle(self, ctx, user: discord.Member = None):
        """Cuddle with someone.."""
        await ctx.trigger_typing()
        res = await self.req("cuddle")
        em = discord.Embed(color=ctx.author.color, title="Cuddle")
        em.description = f"Looks like **{ctx.author.name}** is cuddling with {f'**{str(user.name)}**' if user else 'themselves'}!"
        em.set_image(url=res.url)
        em.set_footer(text=f"Requested by: {str(ctx.author)} | Powered by nekos.life", icon_url=ctx.author.avatar_url)
        await ctx.send(embed=em)

    @commands.command()
    async def poke(self, ctx, user: discord.Member = None):
        """Poke someone.."""
        await ctx.trigger_typing()
        res = await self.req("poke")
        em = discord.Embed(color=ctx.author.color, title="Poke")
        em.description = f"**{ctx.author.name}** poked {f'**{str(user.name)}**' if user else 'themselves'}!"
        em.set_image(url=res.url)
        em.set_footer(text=f"Requested by: {str(ctx.author)} | Powered by nekos.life", icon_url=ctx.author.avatar_url)
        await ctx.send(embed=em)

    @commands.command()
    async def kiss(self, ctx, user: discord.Member = None):
        """Kiss someone.."""
        await ctx.trigger_typing()
        res = await self.req("kiss")
        em = discord.Embed(color=ctx.author.color, title="Kiss")
        em.description = f"**{ctx.author.name}** just kissed {f'**{str(user.name)}**' if user else 'themselves'}!"
        em.set_image(url=res.url)
        em.set_footer(text=f"Requested by: {str(ctx.author)} | Powered by nekos.life", icon_url=ctx.author.avatar_url)
        await ctx.send(embed=em)

    @commands.command()
    async def hug(self, ctx, user: discord.Member = None):
        """Hug someone.."""
        await ctx.trigger_typing()
        res = await self.req("hug")
        em = discord.Embed(color=ctx.author.color, title="Hug")
        em.description = f"**{ctx.author.name}** just hugged {f'**{str(user.name)}**' if user else 'themselves'}!"
        em.set_image(url=res.url)
        em.set_footer(text=f"Requested by: {str(ctx.author)} | Powered by nekos.life", icon_url=ctx.author.avatar_url)
        await ctx.send(embed=em)

    @commands.command()
    async def pat(self, ctx, user: discord.Member = None):
        """Pat someone.."""
        await ctx.trigger_typing()
        res = await self.req("pat")
        em = discord.Embed(color=ctx.author.color, title="Pat")
        em.description = f"**{ctx.author.name}** just patted {f'**{str(user.name)}**' if user else 'themselves'}!"
        em.set_image(url=res.url)
        em.set_footer(text=f"Requested by: {str(ctx.author)} | Powered by nekos.life", icon_url=ctx.author.avatar_url)
        await ctx.send(embed=em)

    @commands.command()
    async def tickle(self, ctx, user: discord.Member = None):
        """Tickle someone.."""
        await ctx.trigger_typing()
        res = await self.req("tickle")
        em = discord.Embed(color=ctx.author.color, title="Tickle")
        em.description = f"**{ctx.author.name}** tickled {f'**{str(user.name)}**' if user else 'themselves'}!"
        em.set_image(url=res.url)
        em.set_footer(text=f"Requested by: {str(ctx.author)} | Powered by nekos.life", icon_url=ctx.author.avatar_url)
        await ctx.send(embed=em)

    @commands.command()
    async def weeb(self, ctx):
        """Get a random pic for weebs."""
        await ctx.trigger_typing()
        res = await self.req("avatar")
        em = discord.Embed(color=ctx.author.color, title="Weeb")
        em.set_image(url=res.url)
        em.set_footer(text=f"Requested by: {str(ctx.author)} | Powered by nekos.life", icon_url=ctx.author.avatar_url)
        await ctx.send(embed=em)

    @commands.command()
    async def smug(self, ctx):
        """Get a random pic of smug anime."""
        await ctx.trigger_typing()
        res = await self.req("smug")
        em = discord.Embed(color=ctx.author.color, title="Smug Anime")
        em.set_image(url=res.url)
        em.set_footer(text=f"Requested by: {str(ctx.author)} | Powered by nekos.life", icon_url=ctx.author.avatar_url)
        await ctx.send(embed=em)

    @commands.command()
    async def waifu(self, ctx):
        """Why not get yourself a waifu?"""
        await ctx.trigger_typing()
        res = await self.req("waifu")
        em = discord.Embed(color=ctx.author.color, title="Waifu")
        em.description = "Found a waifu for you!"
        em.set_image(url=res.url)
        em.set_footer(text=f"Requested by: {str(ctx.author)} | Powered by nekos.life", icon_url=ctx.author.avatar_url)
        await ctx.send(embed=em)

    @commands.command()
    async def neko(self, ctx):
        """Get a random neko."""
        await ctx.trigger_typing()
        res = await self.req("neko")
        img_url = res.url
        em = discord.Embed(color=ctx.author.color, title="Neko")
        em.set_footer(text=f"Requested by: {str(ctx.author)} | Powered by nekos.life", icon_url=ctx.author.avatar_url)
        em.set_image(url=img_url)
        await ctx.send(embed=em)



def setup(bot): 
    bot.add_cog(Anime(bot)) 