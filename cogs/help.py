import discord
import sys
import os
import io
import asyncio
import aiohttp
from discord.ext import commands
from .utils.paginator import HelpPaginator, CannotPaginate


class Help:
    def __init__(self, bot):
       self.bot = bot

    
    @commands.command(name='help')
    async def _help(self, ctx, *, command: str = None):
        """Shows help about a command or the bot"""
        
        try:
            if command is None:
                p = await HelpPaginator.from_bot(ctx)
            else:
                entity = self.bot.get_cog(command) or self.bot.get_command(command)

                if entity is None:
                    clean = command.replace('@', '@\u200b')
                    return await ctx.send(f'Command or category "{clean}" not found.')
                elif isinstance(entity, commands.Command):
                    p = await HelpPaginator.from_command(ctx, entity)
                else:
                    p = await HelpPaginator.from_cog(ctx, entity)

            await p.paginate()
        except Exception as e:
            await ctx.send(e)
            
            
    @commands.command()
    async def testhelp(self, ctx, *, command: str = None):
        """HELP! Not this one, tho..."""
        try:
            if command is None:
                color = discord.Color(value=0x00ff00)
                em = discord.Embed(color=color, title='dat banana bot Help')
                lol = []
                for cog in bot.cogs:
                    lol.append(f"{cog} commands: \n\n")
                    c = bot.get_cog_commands(cog)
                    for cmd in cog:
                        lol.append(f"{cmd.name} \n{cmd.short_doc}")
            em.set_footer("Pulling your hair out? Use the '?' to GET HELP!")
            msg = await ctx.send(embed=em)
            try:
                await msg.add_reaction("\U000021a9") #Fast forward left
                await msg.add_reaction("\U00002b05") #Turn left
                await msg.add_reaction("\U000027a1") #Turn right
                await msg.add_reaction("\U000021aa") #Fast forward right
                await msg.add_reaction("\U0001f6d1") #Stop
                await msg.add_reaction("\U00002049") #Info
            except discord.Forbidden:
                return await ctx.send("Uh-oh! I don't have the 'Add Reactions' permission, so I can't paginate...")
        except Exception as e:
            await ctx.send(f"An error occured. More details: \n\n```{e}```")










def setup(bot): 
    bot.add_cog(Help(bot))   
