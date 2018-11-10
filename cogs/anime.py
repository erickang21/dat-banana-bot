import commands
from discord.ext import commands 
import box
class Anime:
    def __init__(self, bot):
        self.bot = bot

    async def req(self, url):
        res = await self.bot.session.get(f"https://nekos.life/api/v2/img/{url}")
        res = await res.json()
        return box.Box(res)

    @commands.command()
    async def baka(self, ctx):
        """Random anime picture of BAKA."""
        res = await req("baka")
        em = discord.Embed(color=ctx.author.color, title="BAKA!")
        em.set_image(url=res.url)
        em.set_footer(text=f"Requested by: {str(ctx.author)} | Powered by nekos.life", icon_url=ctx.author.avatar_url)
        await ctx.send(embed=em)



def setup(bot): 
    bot.add_cog(Anime(bot)) 