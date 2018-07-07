import discord
from discord.ext import commands


class Level:
    def __init__(self, bot):
        self.bot = bot

    
    @commands.group(invoke_without_subcommand=True)
    async def level(self, ctx):
        return await ctx.send("""
__**Leveling Up**__
**on**: Enable level-ups in this server.
**off**: Disable level-ups in this server.
**balance**: Display the user/your current balance.
""")


    @level.command()
    async def on(self, ctx):
        users = [x.id for x in ctx.guild.members]
        data = {}
        for x in users:
            data[x] = 0
        self.bot.db.level.update_one({"id": ctx.guild.id}, {"$set": {"data": data}}, upsert=True)
        return await ctx.send("Successfully enabled the level-up system for **{}**.".format(ctx.guild.name))


    @level.command()
    async def off(self, ctx):
        users = [str(x.id) for x in ctx.guild.members]
        data = {}
        for x in users:
            data[x] = False
        self.bot.db.level.update_one({"id": ctx.guild.id}, {"$set": {"data": data}}, upsert=True)
        return await ctx.send("Successfully disabled the level-up system for **{}**.".format(ctx.guild.name))


    @level.command()
    async def balance(self, ctx, user: discord.Member = None):
        user = user or ctx.author 
        data = await self.bot.db.level.find_one({"id": ctx.guild.id})
        if not data:
            return await ctx.send("This server doesn't have the level-up system enabled!")
        try:
            match = data['data'][str(ctx.author.id)]
            if match is False: # match could be 0 which returns false, and i don't want that
                return await ctx.send("This server doesn't have the level-up system enabled!")
        except KeyError:
            return await ctx.send("This server doesn't have the level-up system enabled!")
        return await ctx.send(f"**{user.name}** has **{match}** points. Keep it up!")
        

def setup(bot):
    bot.add_cog(Level(bot))