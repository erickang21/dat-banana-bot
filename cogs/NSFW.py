import discord
from discord.ext import commands
from discord.ext.commands import Bot
import random
import lists
from lists import blist, plist, alist


class Info:
    '''NSFW Commands'''

    def __init__(self, bot):
        self.bot = bot



    @command.commands(pass_context = True)
    async def boobs(ctx):
        """Send an image of Boobs"""
        if "nsfw" in ctx.message.channel.name.lower():
            color = ''.join([random.choice('0123456789ABCDEF') for x in range(6)])
            color = int(color, 16)
            embed = discord.Embed(colour=discord.Colour(value=color))
            choice = random.choice(blist)
            embed.set_image(url = choice)
            await ctx.bot.say(embed = embed)
        else:
            msg = ':eyes: | {} Tried to use `boobs` in Non-NSFW Channel | ID: {}'.format(ctx.message.author, ctx.message.author.id)
            await ctx.bot.send_message(discord.utils.get(ctx.message.server.channels, name="logs"), msg)
            await ctx.bot.say(":x: | #nsfw Channel Only! | Action has been logged!")
            
            
            
def setup(bot):
    bot.add_cog(NSFW(bot))
